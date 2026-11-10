"""Run one worker process per model over the GPUs of a Kaggle T4 x2 box.

    ONLY=tag,tag python -u multirun.py jobs.json worker.py [-- extra worker args]      (ONLY empty or unset: every job)

jobs.json: [{"tag": "q3-4b", "tp": 1, "env": {"HARNESS": "4"}, "cands": [{"repo": "...", "backend": "vllm", ...}, ...], ...}, ...]
(env: extra environment of that job's worker processes)
Each candidate runs as `python -u worker.py --job '<job + candidate as json>' extra...` in its own process (a failed vLLM
engine leaves a dirty process); exit code 0 ends the job, anything else tries the next candidate (fp16 -> AWQ, vllm -> hf).
tp 2 jobs run one at a time on both GPUs first; tp 1 jobs then run two at a time, one per GPU. No GPU: one at a time.
After a candidate its Hugging Face cache folder is deleted (Kaggle disk) unless the next candidate uses the same repo, or KEEP_HF=1.
Every worker line is echoed with a [tag] prefix; a summary of which candidate won is written to multirun_summary.json.
"""
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

LOCK = threading.Lock()


def log(msg):
    with LOCK:
        print(msg, flush=True)


def ngpu():
    try:
        return len(subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout.strip().splitlines())
    except FileNotFoundError:
        return 0


def run_job(job, worker, extra, gpus):
    for k, cand in enumerate(job["cands"]):
        spec = dict(job, **cand, cand_index=k)
        spec.pop("cands")
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpus, PYTHONUNBUFFERED="1", LLM_BACKEND=cand.get("backend", "vllm"), **job.get("env", {}))
        t0 = time.time()
        log(f"[{job['tag']}] start candidate {k}: {cand['repo']} ({env['LLM_BACKEND']}) on GPU '{gpus}'")
        p = subprocess.Popen([sys.executable, "-u", worker, "--job", json.dumps(spec, ensure_ascii=False)] + extra,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
        tail = []
        for line in p.stdout:
            line = line.rstrip()
            tail = (tail + [line])[-15:]
            if "it/s]" not in line and "s/it]" not in line:  # drop tqdm bars
                log(f"[{job['tag']}] {line}")
        rc = p.wait()
        nxt = job["cands"][k + 1]["repo"] if k + 1 < len(job["cands"]) else None
        if os.environ.get("KEEP_HF") != "1" and (rc == 0 or nxt != cand["repo"]):  # keep the weights for a retry of the same repo
            hub = Path(os.environ.get("HF_HOME", Path.home() / ".cache/huggingface")) / "hub"
            shutil.rmtree(hub / ("models--" + cand["repo"].replace("/", "--")), ignore_errors=True)
        log(f"[{job['tag']}] candidate {k} rc {rc} after {time.time() - t0:.0f}s")
        if rc == 0:
            return dict(tag=job["tag"], repo=cand["repo"], cand_index=k, ok=True, sec=round(time.time() - t0))
    return dict(tag=job["tag"], ok=False, tail=tail)


def main():
    argv = sys.argv[1:]
    extra = argv[argv.index("--") + 1:] if "--" in argv else []
    argv = argv[:argv.index("--")] if "--" in argv else argv
    jobs = json.load(open(argv[0], encoding="utf-8"))
    worker = argv[1]
    if os.environ.get("ONLY"):
        keep = os.environ["ONLY"].split(",")
        jobs = [j for j in jobs if j["tag"] in keep]
    n = ngpu()
    log(f"[multirun] {len(jobs)} jobs, {n} GPU(s): {[j['tag'] for j in jobs]}")
    done = []
    if n < 2:
        done = [run_job(j, worker, extra, "0" if n else "") for j in jobs]
    else:
        done = [run_job(j, worker, extra, "0,1") for j in jobs if j.get("tp", 1) > 1]
        q = queue.Queue()
        for j in jobs:
            if j.get("tp", 1) == 1:
                q.put(j)

        def drain(g):
            while True:
                try:
                    j = q.get_nowait()
                except queue.Empty:
                    return
                done.append(run_job(j, worker, extra, g))

        ts = [threading.Thread(target=drain, args=(str(g),)) for g in range(2)]
        [t.start() for t in ts]
        [t.join() for t in ts]
    json.dump(done, open("multirun_summary.json", "w"), indent=1)
    log("[multirun] summary: " + json.dumps([(d["tag"], d.get("repo"), d["ok"]) for d in done]))


if __name__ == "__main__":
    main()
