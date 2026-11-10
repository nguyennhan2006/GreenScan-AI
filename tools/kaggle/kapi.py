r"""kapi: run GreenScan notebooks (copied from Zalo AI challenge/kaggle/kapi.py 31/10/2026, itself from FLAG_2027_FourFusion) on Kaggle through the API instead of on this machine (rules: docs/KAGGLE_API_RULES.md).

Credentials: one line per account in an env file OUTSIDE the project (default C:\Users\ASUS\.kaggle\upar_accounts.env, or
FLAG_KAGGLE_ENV):   <username>   <token: KGAT_... or the 32-char legacy key>   [free-text note]
A token is only ever put in the environment of ONE kaggle CLI subprocess (KAGGLE_API_TOKEN, or KAGGLE_USERNAME/KAGGLE_KEY for
a legacy key, with an empty KAGGLE_CONFIG_DIR so no other credential is picked up). It is never printed, logged or written
anywhere. Every push names its account explicitly (no automatic rotation) and is appended to tools/kaggle/kapi_runs.jsonl.

    python tools/kaggle/kapi.py accounts                          # usernames + notes, token check (no secrets shown)
    python tools/kaggle/kapi.py quota [--accounts A,B] [--runs]   # weekly GPU quota per account (Kaggle's endpoint: used /
                                                            # reserved / allowed / reset); --runs: GPU notebooks of 7 days
    python tools/kaggle/kapi.py inventory [--match flag2027]      # datasets / notebooks of every account matching a word
    python tools/kaggle/kapi.py access ACCOUNT owner/dataset ...  # can ACCOUNT read these datasets (needed to attach them)?
    python tools/kaggle/kapi.py find NAME                         # BEFORE any dataset upload: NAME among every account (private
                                                            # + public) and public Kaggle, so nothing is uploaded twice
    python tools/kaggle/kapi.py push NB.ipynb --account A --slug S [--gpu] [--internet] [--datasets o/d,...] [--kernels o/k,...]
                              [--smoke 'K=V;K=V'] [--secret HF_TOKEN] [--title T] [--timeout SEC] [--dry]
                                                            # --secret: KEY=VALUE from C:\Users\ASUS\.kaggle\flag_secrets.env
                                                            # (FLAG_SECRETS_ENV) set as env vars in a first cell; never logged
    python tools/kaggle/kapi.py status A/S | logs A/S | files A/S | output A/S --dest DIR [--pattern REGEX]
    python tools/kaggle/kapi.py nbfind TERM [--files]               # BEFORE pushing: notebooks matching TERM on every account +
                                                            # public, status of their latest run, what their output holds
    python tools/kaggle/kapi.py dscreate FILE... --account A --slug S [--title T] [--dry]   # PRIVATE dataset; refuses a taken slug
    python tools/kaggle/kapi.py privatize OWNER/SLUG [--dry]      # a PRIVATE dataset: every env account as reader (a public one
                                                            # cannot be made private on Kaggle: recreate it)
    python tools/kaggle/kapi.py wait A/S [A/S ...] [--every SEC] [--alive]   # poll until every kernel is finished (status changes
                                                            # printed; --alive: heartbeat verdict of running kernels too)
    python tools/kaggle/kapi.py alive A/S [A/S ...] [--seconds 30] # heartbeat rule: live log of a kernel -> ALIVE / !! stop it
    python tools/kaggle/kapi.py live A/S [--grep RE] [--last N]   # matching lines of a running kernel's live log
    python tools/kaggle/kapi.py delete A/S                         # stuck session: delete the notebook (and its output) as its owner
    python tools/kaggle/kapi.py check ACCOUNT [--datasets ..] [--kernels ..] [--slug S]   # connection check for a run
push refuses a kernel whose latest run is COMPLETE / RUNNING / QUEUED (shows its output) unless --force.
--env 'K=V;K=V' sets environment variables of a real run (GPU kept). --smoke 'K=V;K=V' (pairs separated by ';') inserts a first cell that sets those environment variables (tiny parameters) and forces CPU: a smoke run on Kaggle
costs no GPU hours. Staging folders live in the session scratchpad / %TEMP%, never in the project.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, time, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = Path(os.environ.get("GREENSCAN_KAGGLE_ENV", r"C:\Users\ASUS\.kaggle\acc_kaggle_du_phong.env"))
SECRETS_FILE = Path(os.environ.get("FLAG_SECRETS_ENV", r"C:\Users\ASUS\.kaggle\flag_secrets.env"))   # KEY=VALUE (HF_TOKEN, ...)
RUNLOG = ROOT / "tools/kaggle/kapi_runs.jsonl"
EXTRA_READERS = ROOT / "tools/kaggle/kapi_extra_readers.txt"   # Kaggle users outside the env file who read every private dataset
T4X2 = "NvidiaTeslaT4"                      # kernel-metadata machine_shape for "GPU T4 x2" (kaggle-cli docs/kernels_metadata.md)


def accounts():
    """{username: (token, note)} from the env file; lines starting with # are ignored."""
    out = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 2)
        if len(parts) >= 2:
            out[parts[0]] = (parts[1], parts[2] if len(parts) > 2 else "")
    return out


def secrets():
    """{KEY: VALUE} of the non-Kaggle secrets file (outside the project); empty values are left out. Never printed."""
    out = {}
    if SECRETS_FILE.exists():
        for line in SECRETS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if v.strip():
                    out[k.strip()] = v.strip()
    return out


def mask(text, accs):
    for tok in [t for t, _ in accs.values()] + list(secrets().values()):
        text = text.replace(tok, "<token>")
    return text


def acct_env(account, accs):
    """(env, empty config dir) of ONE subprocess running as ACCOUNT; the caller removes the dir."""
    tok = accs[account][0]
    cfg = Path(tempfile.mkdtemp(prefix="kapi_cfg_"))             # empty config dir: no ~/.kaggle credential leaks in
    env = {k: v for k, v in os.environ.items() if not k.startswith("KAGGLE_")}
    env["KAGGLE_CONFIG_DIR"] = str(cfg)
    if tok.startswith("KGAT_"):
        env["KAGGLE_API_TOKEN"] = tok
    else:
        env["KAGGLE_USERNAME"], env["KAGGLE_KEY"] = account, tok
    env["PYTHONIOENCODING"], env["PYTHONUTF8"] = "utf-8", "1"          # the CLI writes logs with the default codec otherwise
    return env, cfg


def cli(account, args, accs=None, timeout=600):
    """Run `kaggle <args>` as ACCOUNT. Returns (returncode, masked stdout+stderr)."""
    accs = accs or accounts()
    env, cfg = acct_env(account, accs)
    try:
        r = subprocess.run(["kaggle"] + args, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, shell=(os.name == "nt"))
        return r.returncode, mask((r.stdout or "") + (r.stderr or ""), accs)
    except subprocess.TimeoutExpired:                             # a slow API call must not kill a long waiter (12/10)
        return 124, f"timeout after {timeout} s: kaggle {' '.join(args[:3])}"
    finally:
        shutil.rmtree(cfg, ignore_errors=True)


def cmd_accounts(a):
    accs = accounts()
    for u, (tok, note) in accs.items():
        rc, out = cli(u, ["kernels", "list", "--mine", "--page-size", "1"], accs)
        state = "OK" if rc == 0 else "FAILED: " + out.strip().splitlines()[-1][:120] if out.strip() else "FAILED"
        print(f"{u:<16} token {('KGAT' if tok.startswith('KGAT_') else 'legacy key')}  {state:<40} {note}")


def cmd_inventory(a):
    accs = accounts()
    for u in accs:
        print(f"== {u}")
        for kind, args in (("datasets", ["datasets", "list", "--mine", "--search", a.match, "--page-size", "50", "--csv"]),
                           ("kernels", ["kernels", "list", "--mine", "--search", a.match_nb, "--page-size", "50", "--csv"])):
            rc, out = cli(u, args, accs)
            rows = [l for l in out.strip().splitlines()[1:] if l.strip()] if rc == 0 else []
            print(f"  {kind}: " + ("none" if rc == 0 and not rows else "" if rc == 0 else "ERROR " + out.strip()[-160:]))
            for l in rows:
                print("    " + l[:160])


def cmd_find(a):
    """Before creating a dataset: look for its name among the datasets of EVERY account (--mine: private + public) and among
    public Kaggle datasets, so nothing is uploaded twice (user rule 11/10)."""
    accs = accounts()
    hits = []
    for u in accs:
        rc, out = cli(u, ["datasets", "list", "--mine", "--search", a.name, "--page-size", "50", "--csv"], accs)
        if rc == 0:
            hits += [(f"mine:{u}", l) for l in out.strip().splitlines()[1:] if l.strip() and not l.startswith("No datasets")]
        else:
            print(f"!! {u}: {out.strip()[-160:]}")
    rc, out = cli(next(iter(accs)), ["datasets", "list", "--search", a.name, "--page-size", "50", "--csv"], accs)
    if rc == 0:
        hits += [("public", l) for l in out.strip().splitlines()[1:] if l.strip() and not l.startswith("No datasets")]
    seen = set()
    for where, l in hits:
        ref = l.split(",")[0]
        if ref in seen:
            continue
        seen.add(ref)
        print(f"{where:<20} {l[:150]}")
    print(f"{len(seen)} dataset(s) match '{a.name}'" + ("" if seen else ": the name is free"))


def run_status(account, ref, accs=None):
    """'COMPLETE' / 'RUNNING' / 'ERROR' / ... of a kernel's latest run, or None if ACCOUNT cannot see it / it does not exist."""
    rc, out = cli(account, ["kernels", "status", ref], accs, timeout=120)
    m = re.search(r'status "(?:KernelWorkerStatus\.)?([A-Z_]+)"', out)
    return m.group(1) if rc == 0 and m else None


def output_files(account, ref, accs=None, n=200):
    """[(name, size)] of a kernel's latest output (no download)."""
    rc, out = cli(account, ["kernels", "files", ref, "--page-size", str(n), "--csv"], accs, timeout=180)
    if rc != 0:
        return None
    rows = [l.split(",") for l in out.strip().splitlines()[1:] if l.strip()]
    return [(r[0], r[1] if len(r) > 1 else "") for r in rows]


def summarize_files(files):
    """the files that tell what a run produced: progress / reports / selections / submissions / final models"""
    key = re.compile(r"(progress\.json|_report\.txt|_selection\.json|submission.*\.zip|_final_.*|checks\.json|results\.csv)$")
    names = sorted({n.split("/")[-1] for n, _ in files if key.search(n)})
    return "; ".join(names[:12]) + (" ..." if len(names) > 12 else "") if names else "no report / progress / submission file"


def cmd_nbfind(a):
    """Before pushing: notebooks matching TERM on every account (private + public via --mine) and public Kaggle, with the
    status of their latest run and what their output holds. A finished run's output is checked BEFORE running again (user
    rule 11/10)."""
    accs = accounts()
    found = {}
    for u in accs:
        rc, out = cli(u, ["kernels", "list", "--mine", "--search", a.term, "--page-size", "100", "--csv"], accs)
        for l in (out.strip().splitlines()[1:] if rc == 0 else []):
            if l.strip():
                found.setdefault(l.split(",")[0], (u, l))
    rc, out = cli(next(iter(accs)), ["kernels", "list", "--search", a.term, "--page-size", "100", "--csv"], accs)
    for l in (out.strip().splitlines()[1:] if rc == 0 else []):
        if l.strip():
            found.setdefault(l.split(",")[0], (None, l))
    found = {r: v for r, v in found.items() if a.term.lower() in r.split("/")[-1].lower()}   # Kaggle search is fuzzy
    for ref, (u, l) in sorted(found.items()):
        acc = u or (owner(ref) if owner(ref) in accs else next(iter(accs)))
        st = run_status(acc, ref, accs)
        files = output_files(acc, ref, accs) if a.files and st == "COMPLETE" else None
        title = l.split(",")[1] if "," in l else ""
        print(f"{ref:<62} {'env:' + u if u else ('env' if owner(ref) in accs else 'public'):<18} {st or '?':<10} {title[:50]}")
        if files is not None:
            print(f"    output: {len(files)} files: {summarize_files(files)}")
    print(f"{len(found)} notebook(s) match '{a.term}'")


def cmd_check(a):
    """Connection check for a run: every account logs in, can read the given datasets, and the target kernel's state."""
    accs = accounts()
    acc = a.account
    rc, out = cli(acc, ["kernels", "list", "--mine", "--page-size", "1"], accs)
    print(f"{acc}: login {'OK' if rc == 0 else 'FAILED ' + out.strip()[-120:]}")
    for ref in [d for d in (a.datasets or "").split(",") if d]:
        rc, out = cli(acc, ["datasets", "files", ref, "--page-size", "1"], accs)
        print(f"  dataset {ref}: {'readable' if rc == 0 else 'NO ACCESS'}")
    for ref in [k for k in (a.kernels or "").split(",") if k]:
        st = run_status(acc, ref, accs)
        print(f"  kernel {ref}: {st or 'not visible to ' + acc}")
    if a.slug:
        ref = f"{acc}/{a.slug}"
        st = run_status(acc, ref, accs)
        print(f"  target {ref}: {st or 'does not exist yet'}")
        if st == "COMPLETE":
            files = output_files(acc, ref, accs) or []
            print(f"    existing output: {len(files)} files: {summarize_files(files)}  -> check it before pushing again")


def cmd_dscreate(a):
    """Create a PRIVATE dataset ACCOUNT/SLUG from files (a zip is uploaded as is; Kaggle unpacks archives). Runs `find SLUG`
    first and refuses if any account or public Kaggle already has a dataset with that slug (user rule 11/10)."""
    accs = accounts()
    hits = []
    for u in accs:
        rc, out = cli(u, ["datasets", "list", "--mine", "--search", a.slug, "--page-size", "50", "--csv"], accs)
        hits += [l.split(",")[0] for l in (out.strip().splitlines()[1:] if rc == 0 else []) if l.strip()]
    rc, out = cli(a.account, ["datasets", "list", "--search", a.slug, "--page-size", "50", "--csv"], accs)
    hits += [l.split(",")[0] for l in (out.strip().splitlines()[1:] if rc == 0 else []) if l.strip()]
    same = sorted({h for h in hits if h.split("/")[-1] == a.slug})
    if same:
        print(f"not created: {same} already exist(s); add a version to it instead"); sys.exit(3)
    stage = Path(tempfile.mkdtemp(prefix=f"kapi_ds_{a.slug}_"))
    for f in a.files:
        src = Path(f); dst = stage / src.name
        try:
            os.link(src, dst)                                     # same drive: no copy
        except OSError:
            shutil.copy2(src, dst)
    meta = dict(title=a.title or a.slug, id=f"{a.account}/{a.slug}", licenses=[dict(name="other")])
    (stage / "dataset-metadata.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps(dict(meta, staged=str(stage), files=[p.name for p in stage.iterdir()]), indent=1))
    if a.dry:
        print("dry run: nothing created"); return
    rc, out = cli(a.account, ["datasets", "create", "-p", str(stage), "-q"], accs, timeout=7200)   # private (no --public)
    print(out.strip()[-1500:])
    with open(RUNLOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(time=time.strftime("%Y-%m-%d %H:%M"), account=a.account, dataset=meta["id"], private=True,
                                 files=[str(f) for f in a.files], ok=rc == 0)) + "\n")
    shutil.rmtree(stage, ignore_errors=True)
    sys.exit(rc)


def extra_readers():
    """Usernames of kaggle/kapi_extra_readers.txt (one per line, '#' comments): teammates outside the env file (15/10)."""
    if not EXTRA_READERS.exists():
        return []
    return [l.split("#")[0].strip() for l in EXTRA_READERS.read_text(encoding="utf-8").splitlines() if l.split("#")[0].strip()]


def cmd_share(a):
    """Add USER to kaggle/kapi_extra_readers.txt (kept by every later privatize), then privatize each DATASET so USER reads it."""
    if a.user not in extra_readers():
        with open(EXTRA_READERS, "a", encoding="utf-8") as fh:
            fh.write(f"{a.user}  # added {time.strftime('%Y-%m-%d %H:%M')}{(' ' + a.note) if a.note else ''}\n")
    for ds in a.datasets:
        try:
            cmd_privatize(argparse.Namespace(dataset=ds, dry=a.dry))
        except SystemExit as e:
            if e.code not in (0, None):
                print(f"!! {ds}: privatize exit {e.code}")


def cmd_privatize(a):
    """Make OWNER/SLUG private with every other env account (+ kaggle/kapi_extra_readers.txt) as a READER collaborator (API
    runs keep working), license 'other'. Trap: Kaggle's metadata update sets isPrivate = false when the field is absent, so it is always written here.
    Verified afterwards: anonymous view -> 403, another account can still read the files."""
    import urllib.request, urllib.error
    accs = accounts()
    own = owner(a.dataset)
    assert own in accs, f"the owner {own} is not in the env file"
    try:
        code0 = urllib.request.urlopen(f"https://www.kaggle.com/api/v1/datasets/view/{a.dataset}", timeout=60).status
    except urllib.error.HTTPError as e:
        code0 = e.code
    if code0 == 200:      # Kaggle (11/10): "A public dataset can NOT be changed to private" -> delete + recreate private
        print(f"{a.dataset} is PUBLIC: Kaggle cannot make a public dataset private. Recreate it private (`dscreate`, new slug "
              "or after deleting the old one with the owner's OK) and repoint the notebooks."); sys.exit(4)
    d = Path(tempfile.mkdtemp(prefix="kapi_meta_"))
    rc, out = cli(own, ["datasets", "metadata", a.dataset, "-p", str(d)], accs)
    assert rc == 0, out[-300:]
    meta = json.loads((d / "dataset-metadata.json").read_text(encoding="utf-8"))
    info = meta.get("info") or meta
    info["isPrivate"] = True
    info["licenses"] = [dict(name="other")]
    readers = [u for u in accs if u != own] + [u for u in extra_readers() if u not in accs and u != own]
    info["collaborators"] = [dict(username=u, role="reader") for u in readers]
    (d / "dataset-metadata.json").write_text(json.dumps({"info": info}, indent=1), encoding="utf-8")
    if a.dry:
        print(json.dumps(info, indent=1)); return
    rc, out = cli(own, ["datasets", "metadata", a.dataset, "--update", "-p", str(d)], accs)
    print(out.strip()[-300:])
    shutil.rmtree(d, ignore_errors=True)
    try:
        code = urllib.request.urlopen(f"https://www.kaggle.com/api/v1/datasets/view/{a.dataset}", timeout=60).status
    except urllib.error.HTTPError as e:
        code = e.code
    other = next(u for u in accs if u != own)
    rc2, _ = cli(other, ["datasets", "files", a.dataset, "--page-size", "1"], accs)
    print(f"{a.dataset}: anonymous view HTTP {code} ({'PRIVATE' if code in (403, 404) else 'STILL PUBLIC'}); {other} can read: {rc2 == 0}")
    with open(RUNLOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(time=time.strftime("%Y-%m-%d %H:%M"), account=own, privatized=a.dataset, anonymous_http=code,
                                 readers=len(info["collaborators"]), other_can_read=rc2 == 0)) + "\n")


def cmd_wait(a):
    """Poll kernels every EVERY seconds; print each status change; exit when every kernel has a terminal status.
    --alive: also read the live log of every RUNNING kernel at each poll (heartbeat rule, 12/10) and print its verdict
    whenever it changes (a "!!" verdict means: open the notebook page and stop the session)."""
    accs = accounts(); last, lastv = {}, {}
    while True:
        for ref in a.kernels:
            st = run_status(owner(ref), ref, accs) or "?"
            if last.get(ref) != st:
                print(f"{time.strftime('%H:%M')} {ref}: {st}", flush=True); last[ref] = st
            if a.alive and st == "RUNNING":
                r = alive_check(ref, accs, seconds=25)
                if lastv.get(ref) != r["verdict"] or r["verdict"].startswith("!!"):
                    print(f"{time.strftime('%H:%M')} {ref}: {r['verdict']} | {r['n']} log lines, last at t={r['last_t']}s: "
                          f"{r['last'][:120]}", flush=True)
                    lastv[ref] = r["verdict"]
        if all(v not in ("RUNNING", "QUEUED", "?") for v in last.values()):
            return
        time.sleep(a.every)

# ============================================================================ heartbeat rule (user, 12/10)
# Every notebook prints a [boot] line as the FIRST statement of its first code cell (the import cell), before any import.
# A RUNNING notebook with no log line BOOT_MIN minutes after its push, or with no NEW line for SILENT_MIN minutes, is stuck:
# stop its session on the notebook page (the API gives no session id to cancel with) and push again under a new slug.
BOOT = "[boot]"
BOOT_MIN, SILENT_MIN = 10, 45
ALIVE_STATE = ROOT / "tools/kaggle/kapi_alive.json"
LIVE_CODE = """
import sys, json
from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi(); api.authenticate()
for ev in api.kernels_logs_stream(sys.argv[1]):
    print(json.dumps({"t": ev.get("time"), "d": (ev.get("data") or "")[-300:]}), flush=True)
print(json.dumps({"end": True}), flush=True)
"""


def boot_line(name):
    return (f'print("{BOOT} {name} | python", __import__("sys").version.split()[0], "| start", '
            f'__import__("time").strftime("%Y-%m-%d %H:%M:%S"), flush=True)  # heartbeat rule: first output, before any import')


def ensure_boot(nb, name):
    """Put the [boot] print at the top of the first code cell (the import cell) if it is not there; True if added."""
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = c["source"] if isinstance(c["source"], str) else "".join(c["source"])
        if BOOT in "\n".join(src.splitlines()[:3]):
            return False
        c["source"] = boot_line(name) + "\n" + src
        return True
    return False


# Cell rule (user, 19/10): the FIRST statement of EVERY code cell prints a [cell] marker, so the log shows which cell runs.
CELL = "[cell]"


def ensure_cells(nb):
    """Put a [cell] print at the top of every code cell that lacks one -> number added."""
    n, k = 0, 0
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        k += 1
        src = c["source"] if isinstance(c["source"], str) else "".join(c["source"])
        lines = src.splitlines()
        if CELL in "\n".join(lines[:3]):
            continue
        if lines and lines[0].startswith("%%"):                    # a cell magic must stay first (%%writefile would write the print)
            print(f"!! code cell {k} starts with {lines[0].split()[0]}: no {CELL} print possible")
            continue
        j = 0
        while j < len(lines) and (lines[j].startswith(("from __future__", "#!")) or re.match(r"#.*coding[:=]", lines[j])):
            j += 1
        body = [l.strip() for l in lines if l.strip() and BOOT not in l]
        notes = [t for t in (l.lstrip("#").strip(" =-") for l in body if l.startswith("#")) if t]
        name = (notes or body or ["empty"])[0]                     # the first comment says what the cell does, else its first line
        name = re.sub(r"[^\w .,:/()+=-]", "", name)[:60]
        lines.insert(j, f'print("{CELL} {k:02d} {name}", flush=True)')
        c["source"] = "\n".join(lines) + ("\n" if src.endswith("\n") else "")
        n += 1
    return n


def live_log(ref, accs, seconds=30):
    """The session's log (replayed from its start, then live) read for at most SECONDS -> (events, ended, errors)."""
    import threading
    env, cfg = acct_env(owner(ref), accs)
    p = subprocess.Popen([sys.executable, "-c", LIVE_CODE, ref], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8", errors="replace")
    lines = []
    th = threading.Thread(target=lambda: [lines.append(l) for l in p.stdout], daemon=True)
    th.start()
    t0 = time.time()
    while time.time() - t0 < seconds and p.poll() is None:
        time.sleep(0.5)
    if p.poll() is None:
        p.kill()
    th.join(5)
    shutil.rmtree(cfg, ignore_errors=True)
    ev, ended, err = [], False, []
    for l in lines:
        try:
            d = json.loads(l)
        except ValueError:
            err.append(mask(l.rstrip(), accs))
            continue
        if d.get("end"):
            ended = True
        else:
            ev.append(dict(t=d.get("t"), d=mask(d.get("d") or "", accs)))
    return ev, ended, err


def pushed_at(ref):
    """Local time (epoch) of the latest kapi push of REF, or None."""
    best = None
    if RUNLOG.exists():
        for l in RUNLOG.read_text(encoding="utf-8").splitlines():
            d = json.loads(l)
            if d.get("kernel") == ref:
                best = time.mktime(time.strptime(d["time"], "%Y-%m-%d %H:%M"))
    return best


def alive_check(ref, accs, seconds=30):
    """Heartbeat verdict of one kernel from its live log + the previous check (kaggle/kapi_alive.json)."""
    st = run_status(owner(ref), ref, accs) or "?"
    ev, ended, err = live_log(ref, accs, seconds) if st in ("RUNNING", "COMPLETE", "ERROR") else ([], False, [])
    lines = [e for e in ev if e["d"].strip()]
    boot = any(BOOT in e["d"] for e in lines[:50])
    now = time.time()
    state = json.loads(ALIVE_STATE.read_text(encoding="utf-8")) if ALIVE_STATE.exists() else {}
    prev = state.get(ref, {})
    since = prev["since"] if prev.get("n") == len(lines) and "since" in prev else now
    state[ref] = dict(n=len(lines), since=since, checked=now)
    ALIVE_STATE.write_text(json.dumps(state, indent=1), encoding="utf-8")
    pa = pushed_at(ref)
    run_min = (now - pa) / 60 if pa else None
    silent_min = (now - since) / 60
    url = f"https://www.kaggle.com/code/{ref}"
    if st != "RUNNING":
        verdict = st
    elif not lines and run_min is not None and run_min >= BOOT_MIN:
        verdict = f"!! NO LOG {run_min:.0f} min after push -> stop the session at {url}"
    elif not lines:
        verdict = "starting (no log yet)"
    elif silent_min >= SILENT_MIN:
        verdict = f"!! NO NEW LOG for {silent_min:.0f} min -> check, and stop the session at {url} if stuck"
    else:
        verdict = "ALIVE" + ("" if boot else " (no [boot] line: notebook built before the rule)")
    last = lines[-1] if lines else dict(t=None, d="")
    return dict(ref=ref, status=st, verdict=verdict, n=len(lines), boot=boot,
                last_t=None if last["t"] is None else round(float(last["t"])), last=last["d"].strip(), ended=ended,
                errors=err[-3:], run_min=None if run_min is None else round(run_min))


def cmd_alive(a):
    accs = accounts()
    for ref in a.kernels:
        r = alive_check(ref, accs, a.seconds)
        print(f"{ref}: {r['status']} | {r['verdict']}")
        print(f"  log lines {r['n']} | [boot] seen {r['boot']} | pushed {r['run_min']} min ago | "
              f"last line at t={r['last_t']}s: {r['last'][:160]}")
        for e in r["errors"]:
            print("  stream:", e[:200])


def cmd_live(a):
    """Lines of a running kernel's live log matching --grep (regex), last --last of them."""
    ev, ended, err = live_log(a.kernel, accounts(), a.seconds)
    hits = [e for e in ev if re.search(a.grep, e["d"])]
    for e in hits[-a.last:]:
        print(f"t={e['t']:.0f}s {e['d'].rstrip()[:400]}" if isinstance(e["t"], (int, float)) else e["d"].rstrip()[:400])
    print(f"({len(ev)} lines read, {len(hits)} matched, ended={ended})")


def cmd_access(a):
    accs = accounts()
    for ref in a.refs:
        rc, out = cli(a.account, ["datasets", "files", ref, "--page-size", "1"], accs)
        print(f"{a.account} -> {ref}: {'readable' if rc == 0 else 'NO ACCESS (' + out.strip().splitlines()[-1][:100] + ')'}")


def smoke_cell(kv, head="# smoke run (kapi --smoke): tiny parameters, CPU"):
    lines = [head, "import os"]
    lines += [f"os.environ[{k!r}] = {v!r}" for k, v in kv]
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": "\n".join(lines)}


def secret_cell(names):
    """First cell setting the named secrets as environment variables (values from SECRETS_FILE; the cell prints nothing)."""
    sec = secrets()
    missing = [n for n in names if n not in sec]
    if missing:
        sys.exit(f"--secret: {missing} empty or missing in {SECRETS_FILE} (fill KEY=VALUE there; never in the project)")
    lines = ["# secrets (kapi --secret): environment variables only; never print them", "import os"]
    lines += [f"os.environ[{n!r}] = {sec[n]!r}" for n in names]
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": "\n".join(lines)}


def cmd_push(a):
    accs = accounts()
    assert a.account in accs, f"unknown account {a.account}"
    nb = json.loads(Path(a.notebook).read_text(encoding="utf-8"))
    if ensure_boot(nb, Path(a.notebook).stem):                    # heartbeat rule (12/10): the import cell prints first
        print(f"{BOOT} print added to the first code cell of {Path(a.notebook).name} (the builder should emit it)")
    smoke = [tuple(x.split("=", 1)) for x in a.smoke.split(";") if x.strip()] if a.smoke else []     # K=V;K=V (values may hold commas)
    if smoke:
        nb["cells"].insert(0, smoke_cell(smoke))
    envs = [tuple(x.split("=", 1)) for x in a.env.split(";") if x.strip()] if a.env else []        # 16/10: real-run parameters, GPU kept
    if envs:
        nb["cells"].insert(0, smoke_cell(envs, "# run parameters (kapi --env): environment variables of this run"))
    names = [n for n in (a.secret or "").split(",") if n]
    if names:
        nb["cells"].insert(0, secret_cell(names))
    added = ensure_cells(nb)                                       # cell rule (19/10): every code cell prints [cell] first
    if added:
        print(f"{CELL} print added to {added} code cells")
    gpu = a.gpu and not smoke
    if not a.internet and "pip install" in json.dumps(nb):           # 31/10: a run pushed without internet lost its pip install
        a.internet = True
        print("internet enabled: the notebook runs pip install")
    slug = a.slug + ("-smoke" if smoke and not a.slug.endswith("-smoke") else "")
    stage = Path(tempfile.mkdtemp(prefix=f"kapi_{slug}_"))
    code = stage / f"{slug}.ipynb"
    code.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    slugify = lambda t: re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    title = a.title if a.title and slugify(a.title) == slug else slug     # Kaggle derives the slug from the title: keep them equal
    meta = dict(id=f"{a.account}/{slug}", title=title, code_file=code.name, language="python", kernel_type="notebook",
                is_private=True, enable_gpu=gpu, enable_internet=a.internet, machine_shape=(a.accelerator or T4X2) if gpu else "",
                dataset_sources=[d for d in (a.datasets or "").split(",") if d],
                kernel_sources=[k for k in (a.kernels or "").split(",") if k], competition_sources=[], model_sources=[])
    (stage / "kernel-metadata.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    md5 = hashlib.md5(code.read_bytes()).hexdigest()
    print(json.dumps(dict(meta, staged=str(stage), notebook_md5=md5), indent=1))
    st = run_status(a.account, meta["id"], accs)              # an existing run is checked BEFORE running again (11/10)
    if st:
        print(f"existing kernel {meta['id']}: latest run {st}")
        if st == "COMPLETE":
            files = output_files(a.account, meta["id"], accs) or []
            print(f"  its output: {len(files)} files: {summarize_files(files)}")
        if st in ("COMPLETE", "RUNNING", "QUEUED") and not a.force:
            print("not pushed: check that run / its output first (`kapi.py files|output`), or pass --force to start a new version")
            sys.exit(3)
    if a.dry:
        if names:
            shutil.rmtree(stage, ignore_errors=True)                 # the staged notebook holds the secret
        print("dry run: nothing pushed"); return
    for ref in meta["dataset_sources"]:                          # the account must be able to read every input
        for _ in range(4):                                       # a network timeout is not a missing permission: retry
            rc, out = cli(a.account, ["datasets", "files", ref, "--page-size", "1"], accs)
            if rc == 0 or "timed out" not in out:
                break
            time.sleep(10)
        assert rc == 0, f"{a.account} cannot read {ref}: {out.strip()[-200:]}"
    args = ["kernels", "push", "-p", str(stage)] + (["--accelerator", a.accelerator or T4X2] if gpu else []) + (["-t", str(a.timeout)] if a.timeout else [])
    rc, out = cli(a.account, args, accs, timeout=900)
    print(out.strip())
    if names:
        shutil.rmtree(stage, ignore_errors=True)                     # the staged notebook holds the secret
    with open(RUNLOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(time=time.strftime("%Y-%m-%d %H:%M"), account=a.account, kernel=meta["id"], source=str(a.notebook),
                                 notebook_md5=md5, gpu=gpu, smoke=dict(smoke), secrets=names, datasets=meta["dataset_sources"],
                                 kernels=meta["kernel_sources"], ok=rc == 0)) + "\n")
    sys.exit(rc)


def gpu_hours(account, accs, days=7):
    """[(ref, last run UTC, hours)] of the GPU notebooks ACCOUNT ran in the last DAYS days: enable_gpu from the pulled metadata,
    run length = the last `time` of the run log (latest version only). Kaggle exposes no quota endpoint, so this is a LOWER
    bound of the GPU hours used (earlier versions of a re-pushed notebook and interactive editor sessions are invisible)."""
    import csv, io
    from datetime import datetime, timedelta, timezone
    since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)     # lastRunTime is UTC
    rc, out = cli(account, ["kernels", "list", "--mine", "--page-size", "100", "--sort-by", "dateRun", "--csv"], accs, timeout=240)
    if rc != 0:
        return None
    rows = []
    for r in csv.DictReader(io.StringIO("\n".join(l for l in out.splitlines() if l.strip()))):
        try:
            t = datetime.strptime(r["lastRunTime"][:19], "%Y-%m-%d %H:%M:%S")
        except (KeyError, ValueError):
            continue
        if not r.get("ref") or t < since:
            continue
        d = Path(tempfile.mkdtemp(prefix="kapi_meta_"))
        try:
            cli(account, ["kernels", "pull", r["ref"], "-m", "-p", str(d)], accs, timeout=240)
            m = d / "kernel-metadata.json"
            gpu = m.exists() and bool(json.loads(m.read_text(encoding="utf-8")).get("enable_gpu"))
        finally:
            shutil.rmtree(d, ignore_errors=True)
        if not gpu:
            continue
        rc3, lg = cli(account, ["kernels", "logs", r["ref"]], accs, timeout=300)
        try:
            L = json.loads(lg[lg.index("["):])
            h = max(e.get("time", 0) for e in L) / 3600 if L else 0.0
        except ValueError:
            h = None
        rows.append((r["ref"], t.strftime("%m-%d %H:%M"), h))
    return rows


def quota_stats(account, accs):
    """(used h, reserved h, allowed h, refresh UTC) of ACCOUNT's weekly GPU quota from Kaggle's own endpoint
    (kagglesdk KernelsApiService.GetAcceleratorQuotaStatistics); the token stays inside this process."""
    from kagglesdk import KaggleClient
    from kagglesdk.kernels.types.kernels_api_service import ApiGetAcceleratorQuotaStatisticsRequest
    tok = accs[account][0]
    kw = dict(api_token=tok) if tok.startswith("KGAT_") else dict(username=account, password=tok)
    h = lambda td: round(td.total_seconds() / 3600, 1) if td is not None else 0.0
    with KaggleClient(**kw) as c:
        r = c.kernels.kernels_api_client.get_accelerator_quota_statistics(ApiGetAcceleratorQuotaStatisticsRequest())
    g = r.gpu_quota
    return h(g.time_used), h(g.time_reserved), h(g.total_time_allowed), r.quota_refresh_time


def cmd_quota(a):
    """Weekly GPU quota of every account (Kaggle's endpoint: used / reserved by running sessions / allowed / reset time).
    Spread runs over accounts by hand from this table: every push still names its account explicitly. --runs adds the GPU
    notebooks of the last 7 days with their run length (from the logs)."""
    import concurrent.futures as cf
    accs = accounts()
    names = [u for u in accs if not a.accounts or u in a.accounts.split(",")]

    def one(u):
        try:
            return u, quota_stats(u, accs), None
        except Exception as e:
            return u, None, mask(f"{type(e).__name__}: {e}", accs)[:120]
    with cf.ThreadPoolExecutor(7) as ex:
        res = list(ex.map(one, names))
    print(f"{'account':<18} {'used h':>7} {'reserved h':>10} {'allowed h':>9} {'left h':>7}  resets (UTC)")
    for u, q, err in sorted(res, key=lambda x: -(x[1][2] - x[1][0] - x[1][1]) if x[1] else 99):
        if q is None:
            print(f"{u:<18} ERROR {err}"); continue
        used, res_, allowed, when = q
        print(f"{u:<18} {used:>7.1f} {res_:>10.1f} {allowed:>9.1f} {allowed - used - res_:>7.1f}  {when}")
        if a.runs:
            for r, t, hh in (gpu_hours(u, accs, 7) or []):
                print(f"    {t}  {'?' if hh is None else f'{hh:5.2f}'} h  {r}")


def owner(ref):
    return ref.split("/")[0]


def cmd_status(a):
    rc, out = cli(owner(a.kernel), ["kernels", "status", a.kernel]); print(out.strip()); sys.exit(rc)


def cmd_logs(a):
    rc, out = cli(owner(a.kernel), ["kernels", "logs", a.kernel], timeout=300); print(out.strip()[-a.tail:]); sys.exit(rc)


def cmd_output(a):
    if a.pattern and "|" in a.pattern:                                # the CLI runs through cmd: "|" becomes a pipe
        sys.exit(r"--pattern must not contain '|' (cmd pipe); use a character class, e.g. '\.[jlt][a-z]*$'")
    Path(a.dest).mkdir(parents=True, exist_ok=True)
    args = ["kernels", "output", a.kernel, "-p", a.dest, "-o"] + (["--file-pattern", a.pattern] if a.pattern else [])
    rc, out = cli(owner(a.kernel), args, timeout=3600); print(out.strip()[-2000:]); sys.exit(rc)


def cmd_delete(a):
    """Delete a notebook (its versions and output too) as its owner: the way to stop a stuck session (14/10), since the API has
    no session id to cancel with. Only for notebooks with nothing to keep (a smoke test, a run that never logged)."""
    rc, out = cli(owner(a.kernel), ["kernels", "status", a.kernel], timeout=120)
    print("before:", out.strip().splitlines()[-1] if out.strip() else rc)
    rc, out = cli(owner(a.kernel), ["kernels", "delete", a.kernel, "-y"], timeout=180)
    print(out.strip()[-500:]); sys.exit(rc)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("accounts").set_defaults(fn=cmd_accounts)
    q = sp.add_parser("quota"); q.add_argument("--accounts"); q.add_argument("--runs", action="store_true"); q.set_defaults(fn=cmd_quota)
    q = sp.add_parser("inventory"); q.add_argument("--match", default="greenscan"); q.add_argument("--match-nb", default="gs-")
    q.set_defaults(fn=cmd_inventory)
    q = sp.add_parser("access"); q.add_argument("account"); q.add_argument("refs", nargs="+"); q.set_defaults(fn=cmd_access)
    q = sp.add_parser("find"); q.add_argument("name"); q.set_defaults(fn=cmd_find)
    q = sp.add_parser("wait"); q.add_argument("kernels", nargs="+"); q.add_argument("--every", type=int, default=900)
    q.add_argument("--alive", action="store_true"); q.set_defaults(fn=cmd_wait)
    q = sp.add_parser("live"); q.add_argument("kernel"); q.add_argument("--grep", default="."); q.add_argument("--last", type=int, default=20)
    q.add_argument("--seconds", type=int, default=25); q.set_defaults(fn=cmd_live)
    q = sp.add_parser("alive"); q.add_argument("kernels", nargs="+"); q.add_argument("--seconds", type=int, default=30)
    q.set_defaults(fn=cmd_alive)
    q = sp.add_parser("privatize"); q.add_argument("dataset"); q.add_argument("--dry", action="store_true"); q.set_defaults(fn=cmd_privatize)
    q = sp.add_parser("share"); q.add_argument("user"); q.add_argument("datasets", nargs="+"); q.add_argument("--note", default="")
    q.add_argument("--dry", action="store_true"); q.set_defaults(fn=cmd_share)
    q = sp.add_parser("dscreate"); q.add_argument("files", nargs="+"); q.add_argument("--account", required=True)
    q.add_argument("--slug", required=True); q.add_argument("--title"); q.add_argument("--dry", action="store_true"); q.set_defaults(fn=cmd_dscreate)
    q = sp.add_parser("push"); q.add_argument("notebook"); q.add_argument("--account", required=True); q.add_argument("--slug", required=True)
    q.add_argument("--title"); q.add_argument("--gpu", action="store_true"); q.add_argument("--accelerator", help="with --gpu: machine shape, default NvidiaTeslaT4 (T4 x2); e.g. NvidiaTeslaP100 when the T4 queue is long"); q.add_argument("--internet", action="store_true")
    q.add_argument("--datasets"); q.add_argument("--kernels"); q.add_argument("--smoke"); q.add_argument("--timeout", type=int)
    q.add_argument("--env", help="'K=V;K=V': environment variables of a real run (first cell; unlike --smoke, keeps --gpu)")
    q.add_argument("--secret", help="names in the secrets file (e.g. HF_TOKEN), set as environment variables in a first cell")
    q.add_argument("--dry", action="store_true"); q.add_argument("--force", action="store_true"); q.set_defaults(fn=cmd_push)
    q = sp.add_parser("nbfind"); q.add_argument("term"); q.add_argument("--files", action="store_true"); q.set_defaults(fn=cmd_nbfind)
    q = sp.add_parser("check"); q.add_argument("account"); q.add_argument("--datasets"); q.add_argument("--kernels"); q.add_argument("--slug")
    q.set_defaults(fn=cmd_check)
    q = sp.add_parser("files"); q.add_argument("kernel"); q.set_defaults(fn=lambda a: [print(f"{n}  {sz}") for n, sz in (output_files(owner(a.kernel), a.kernel) or [])])
    for name, fn in (("status", cmd_status), ("logs", cmd_logs)):
        q = sp.add_parser(name); q.add_argument("kernel"); q.add_argument("--tail", type=int, default=6000); q.set_defaults(fn=fn)
    q = sp.add_parser("delete"); q.add_argument("kernel"); q.set_defaults(fn=cmd_delete)
    q = sp.add_parser("output"); q.add_argument("kernel"); q.add_argument("--dest", required=True); q.add_argument("--pattern")
    q.set_defaults(fn=cmd_output)
    a = p.parse_args(); a.fn(a)
