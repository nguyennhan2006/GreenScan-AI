"""Run-time switch for the language-model stages (model-mode-v1, D-2026-11-16-01).

The stages already exist behind environment variables (settings.py: QUANTUM_LLM_STANCE, QUANTUM_VERIFY,
QUANTUM_ASSIST_EXPLAIN, QUANTUM_ASSIST_ATTRIBUTES) and the router already knows where each task goes
(configs/routing.yaml). What was missing is a way to turn them on while the server is running, so a demo
can show the same documents with and without a model. This module writes those variables; every run reads
them afresh through load_settings() / ModelGateway().

Three modes:
  rules  no model is called; rules and arithmetic only (the default of the offline profile).
  local  a model on this machine reads the hard pairs; nothing leaves the machine.
  cloud  a hosted model reads them; allowed for published documents only, and the screen says so.

In every mode SUPPORTED and CONTRADICTED are written by the rules and the arithmetic only
(settings.verification.llm_stance_decisive stays False). A model adds a reading and a plain-language explanation;
where it reads a passage differently from the rules the claim goes to a person (requires_llm_review), and an
intermediate verdict can move: on sample case A one claim goes from UNSUPPORTED to PARTIALLY_SUPPORTED.
"""
from __future__ import annotations

import os
import time

import httpx

from quantum_gw import settings as _settings  # noqa: F401 - loads .env and the profile first

MODES = ("rules", "local", "cloud")
POLICY_ID = "model-mode-v1"
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen3:4b-instruct-2507-q4_K_M"
CLOUD_KEYS = (("groq", "GROQ_API_KEY"), ("fpt", "FPT_LLM_API_KEY"))

_STAGES_ON = {"QUANTUM_LLM_STANCE": "on_ambiguous", "QUANTUM_VERIFY": "dual",
              "QUANTUM_ASSIST_EXPLAIN": "queue", "QUANTUM_ASSIST_ATTRIBUTES": "1"}
_STAGES_OFF = {"QUANTUM_LLM_STANCE": "off", "QUANTUM_VERIFY": "rules",
               "QUANTUM_ASSIST_EXPLAIN": "off", "QUANTUM_ASSIST_ATTRIBUTES": "0"}
_TOUCHED = (*_STAGES_ON, "QUANTUM_PROFILE", "LLM_PROVIDER", "LLM_FALLBACK_ORDER", "LOCAL_LLM_PROVIDER",
            "LOCAL_LLM_BASE_URL", "LOCAL_LLM_MODEL", "LOCAL_LLM_TIMEOUT_SECONDS")
# What .env and the profile set before anyone pressed a button; "rules" goes back to the provider part of it.
_BASELINE = {key: os.environ.get(key) for key in _TOUCHED}

LABELS = {
    "rules": ("Chỉ luật và phép tính", "Không gọi mô hình nào. Nhanh nhất; tài liệu không rời máy."),
    "local": ("Mô hình chạy trên máy này", "Mô hình mở đọc các cặp khó ngay trên máy; tài liệu không rời máy. Chậm trên máy không có GPU."),
    "cloud": ("Mô hình trên đám mây", "Nhanh hơn, nhưng đoạn trích được gửi ra ngoài: chỉ dùng cho tài liệu đã công bố."),
}


def _restore(keys) -> None:
    for key in keys:
        if _BASELINE.get(key) is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = _BASELINE[key]


def _local_env() -> dict[str, str]:
    """The server's own local model when .env names one (gpu / selfhost), otherwise Ollama on this machine."""
    if _BASELINE.get("LOCAL_LLM_BASE_URL"):
        return {key: _BASELINE[key] for key in ("LOCAL_LLM_PROVIDER", "LOCAL_LLM_BASE_URL", "LOCAL_LLM_MODEL")
                if _BASELINE.get(key)}
    return {"LOCAL_LLM_PROVIDER": "ollama",
            "LOCAL_LLM_BASE_URL": os.environ.get("QUANTUM_LOCAL_MODEL_URL", DEFAULT_OLLAMA_URL),
            "LOCAL_LLM_MODEL": os.environ.get("QUANTUM_LOCAL_MODEL", DEFAULT_OLLAMA_MODEL),
            # A 4B model on a laptop CPU needs minutes for a long prompt; 180 s cut readings short.
            "LOCAL_LLM_TIMEOUT_SECONDS": os.environ.get("QUANTUM_LOCAL_MODEL_TIMEOUT", "600")}


def _cloud_provider() -> str | None:
    return next((name for name, key in CLOUD_KEYS if os.environ.get(key)), None)


def _ollama_models(url: str) -> list[str] | None:
    try:
        with httpx.Client(timeout=1.5) as client:
            body = client.get(f"{url.rstrip('/')}/api/tags").json()
        return [m.get("name", "") for m in body.get("models", [])]
    except Exception:  # noqa: BLE001 - not running, not installed, or not Ollama at all
        return None


def availability() -> dict[str, dict]:
    """Can each mode be turned on right now, and if not, what is missing (shown next to the button)."""
    local = _local_env()
    if local.get("LOCAL_LLM_PROVIDER") == "ollama":
        models = _ollama_models(local["LOCAL_LLM_BASE_URL"])
        if models is None:
            local_state = {"available": False, "reason": "Chưa thấy Ollama chạy trên máy này (mở Ollama rồi tải lại trang)."}
        elif local["LOCAL_LLM_MODEL"] not in models:
            local_state = {"available": False, "reason": f"Ollama chưa có mô hình {local['LOCAL_LLM_MODEL']} (chạy: ollama pull {local['LOCAL_LLM_MODEL']})."}
        else:
            local_state = {"available": True, "reason": ""}
    else:
        local_state = {"available": True, "reason": ""}
    local_state["model"] = local.get("LOCAL_LLM_MODEL", "")
    cloud = _cloud_provider()
    cloud_model = ""
    if cloud:
        from quantum_gw.providers.router import ModelGateway

        policy = ModelGateway().routing.get("qualitative_stance")
        cloud_model = ((policy.models or {}).get(cloud) if policy else None) or cloud
    return {
        "rules": {"available": True, "reason": "", "model": ""},
        "local": local_state,
        "cloud": {"available": cloud is not None, "model": cloud_model,
                  "reason": "" if cloud else "Chưa có khoá truy cập dịch vụ mô hình trong tệp .env."},
    }


def set_mode(mode: str) -> str:
    """Point the next run at `mode`. Raises ValueError when the mode is unknown or cannot be served."""
    mode = (mode or "").strip().lower()
    if mode not in MODES:
        raise ValueError(f"mode must be one of {list(MODES)}, not {mode!r}")
    state = availability()[mode]
    if not state["available"]:
        raise ValueError(state["reason"])
    _restore(_TOUCHED)
    if mode == "rules":
        os.environ.update(_STAGES_OFF)
        return mode
    os.environ.update(_STAGES_ON)
    if mode == "local":
        os.environ.update({"QUANTUM_PROFILE": "offline", **_local_env()})
    else:
        provider = _cloud_provider() or ""
        os.environ.update({"QUANTUM_PROFILE": "cloud", "LLM_PROVIDER": provider, "LLM_FALLBACK_ORDER": provider,
                           "LOCAL_LLM_BASE_URL": ""})
    return mode


def describe(verification) -> dict | None:
    """Which stages of a run have a model behind them: {"mode", "routes": {task: "provider:model"}}; None for rules."""
    from quantum_gw.providers.router import ModelGateway

    v = verification
    stages = [task for on, task in ((v.llm_stance == "on_ambiguous", "qualitative_stance"),
                                    (v.verify_mode == "dual", "ir_reading"),
                                    (v.assist_explain != "off", "claim_explanation"),
                                    (v.assist_attributes, "claim_normalization")) if on]
    gateway = ModelGateway()
    routes = {task: route[0] for task in stages if (route := gateway.route(task))}
    if not routes:
        return None
    local = all(r.split(":", 1)[0] in {"local", "ollama"} for r in routes.values())
    return {"mode": "local" if local else "cloud", "routes": routes, "policy": POLICY_ID}


def current_mode() -> str:
    """What a run started now would do, read from the same settings the run reads."""
    from quantum_gw.settings import load_settings

    described = describe(load_settings().verification)
    return described["mode"] if described else "rules"


TEST_CLAIM = "Công ty đã sử dụng hoàn toàn 500 tỷ đồng trái phiếu xanh cho các dự án năng lượng tái tạo."
TEST_EVIDENCE = "Đến 31/12/2024, 320 tỷ đồng đã giải ngân cho dự án điện mặt trời; 180 tỷ đồng còn lại chưa phân bổ."


def test_call() -> dict:
    """One short live call through the same route the hard pairs use, so a viewer sees the model answer."""
    from quantum_gw.providers.router import ModelGateway

    gateway = ModelGateway()
    route = gateway.route("qualitative_stance")
    if current_mode() == "rules" or not route:
        return {"ok": False, "detail": "Đang ở chế độ chỉ luật: không có mô hình nào để gọi."}
    messages = [
        {"role": "system", "content": "Bạn giúp kiểm toán viên đọc bằng chứng. Trả lời bằng tiếng Việt, tối đa hai câu."},
        {"role": "user", "content": f"Tuyên bố: {TEST_CLAIM}\nBằng chứng: {TEST_EVIDENCE}\n"
                                    "Bằng chứng ủng hộ, mâu thuẫn hay không liên quan đến tuyên bố? Nêu lý do ngắn gọn."},
    ]
    started = time.time()
    try:
        response = gateway.generate(messages, task_type="qualitative_stance")
    except Exception as exc:  # noqa: BLE001 - shown to the person who pressed the button
        return {"ok": False, "detail": str(exc)[:300], "route": route, "seconds": round(time.time() - started, 1)}
    return {"ok": True, "provider": response.provider, "model": response.model, "answer": response.text.strip()[:600],
            "seconds": round(time.time() - started, 1), "claim": TEST_CLAIM, "evidence": TEST_EVIDENCE, "route": route}
