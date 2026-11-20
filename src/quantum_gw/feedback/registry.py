"""Model registry and promotion gate (feedback-loop-v1, tier 4): champion vs challenger.

A trained stance model is registered as a `candidate` together with its scores
and the champion's scores on the same held-out pairs. It can be `promoted` only
when all of these hold, and the reasons are kept either way:

1. enough held-out pairs to mean something (MIN_HOLDOUT);
2. macro-F1 not below the champion's;
3. no more false CONTRADICTS than the champion (the "vu oan" error);
4. no more false SUPPORTS than the champion (the "bỏ lọt" error);
5. a named person approves it (four-eyes: not the person who trained it).

A promoted model is the only kind `feedback.local_stance_model` accepts, and its
weights must still hash to what was registered, so a swapped file is refused.
Promoting a model retires the previous one; nothing is deleted, the registry is
the history. Even a promoted model only answers the pairs the rules escalate,
with the same guards as the LLM (method "llm": not decisive on its own).
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

MIN_HOLDOUT = 30
CANDIDATE, PROMOTED, RETIRED = "candidate", "promoted", "retired"


def read(path: str | Path) -> dict:
    path = Path(path)
    if not path.is_file():
        return {"schema": "stance-registry-v1", "models": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: str | Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def gate(champion: dict, challenger: dict) -> dict:
    reasons, passed = [], True

    def check(ok: bool, text: str) -> None:
        nonlocal passed
        reasons.append(("đạt: " if ok else "KHÔNG đạt: ") + text)
        passed = passed and ok

    check(challenger["answered"] >= MIN_HOLDOUT,
          f"{challenger['answered']} cặp giữ lại được chấm (cần ≥ {MIN_HOLDOUT})")
    cf1, hf1 = champion.get("macro_f1") or 0.0, challenger.get("macro_f1") or 0.0
    check(hf1 >= cf1, f"macro-F1 {hf1:.3f} so với nhà vô địch {cf1:.3f}")
    check(challenger["false_contradicts"] <= champion["false_contradicts"],
          f"CONTRADICTS sai {challenger['false_contradicts']} so với {champion['false_contradicts']}")
    check(challenger["false_supports"] <= champion["false_supports"],
          f"SUPPORTS sai {challenger['false_supports']} so với {champion['false_supports']}")
    return {"passed": passed, "reasons": reasons}


def weights_hash(model_dir: str | Path) -> str | None:
    weights = Path(model_dir) / "weights.npz"
    return hashlib.sha256(weights.read_bytes()).hexdigest() if weights.is_file() else None


def register(path: str | Path, model_dir: str | Path, *, champion: dict, challenger: dict, data: dict,
             trained_by: str, kind: str, note: str = "") -> dict:
    registry = read(path)
    model_id = Path(model_dir).name
    if any(m["model_id"] == model_id for m in registry["models"]):
        raise ValueError(f"model {model_id} is already registered; train into a new folder")
    entry = {
        "model_id": model_id, "path": str(Path(model_dir)).replace("\\", "/"), "kind": kind,
        "registered_at": datetime.now(UTC).isoformat(), "trained_by": trained_by, "data": data,
        "weights_sha256": weights_hash(model_dir), "champion": champion, "challenger": challenger,
        "gate": gate(champion, challenger), "status": CANDIDATE, "approved_by": "", "approved_at": "", "note": note,
    }
    registry["models"].append(entry)
    _write(path, registry)
    return entry


def promote(path: str | Path, model_id: str, approved_by: str) -> dict:
    registry = read(path)
    entry = next((m for m in registry["models"] if m["model_id"] == model_id), None)
    if entry is None:
        raise ValueError(f"no model {model_id} in {path}")
    approved_by = (approved_by or "").strip()
    if not approved_by:
        raise ValueError("promotion needs the name of the person who approves it")
    if approved_by.casefold() == (entry.get("trained_by") or "").strip().casefold():
        raise ValueError("the person who trained a model cannot also approve it")
    if not entry["gate"]["passed"]:
        raise ValueError("the model did not pass the gate: " + "; ".join(entry["gate"]["reasons"]))
    if weights_hash(entry["path"]) != entry["weights_sha256"]:
        raise ValueError("the weights on disk no longer match what was registered")
    for other in registry["models"]:
        if other["status"] == PROMOTED:
            other["status"] = RETIRED
            other["retired_at"] = datetime.now(UTC).isoformat()
    entry.update(status=PROMOTED, approved_by=approved_by, approved_at=datetime.now(UTC).isoformat())
    _write(path, registry)
    return entry


def promoted_entry(path: str | Path, model_dir: str | Path) -> dict:
    """The registry entry for `model_dir` if it is promoted and untampered; raises otherwise."""
    wanted = str(Path(model_dir)).replace("\\", "/").rstrip("/")
    for entry in read(path)["models"]:
        if entry["path"].rstrip("/") == wanted or Path(entry["path"]).resolve() == Path(model_dir).resolve():
            if entry["status"] != PROMOTED:
                raise ValueError(f"model {entry['model_id']} is {entry['status']}, not promoted")
            if weights_hash(model_dir) != entry["weights_sha256"]:
                raise ValueError(f"model {entry['model_id']}: weights changed since registration")
            return entry
    raise ValueError(f"{model_dir} is not in the model registry {path}")
