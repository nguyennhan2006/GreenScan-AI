"""Scope guard + task router for free-text requests (D-2026-11-13-01, registration prompt_router_v1).

route(request) -> Route(status, category, warning, tasks, slots, source):
  status "ok"            in scope; `tasks` say which product step(s) to run, `slots` what the request gave
  status "need_info"     in scope but a required slot is missing (e.g. verify_claim without the claim text)
  status "out_of_scope"  outside GreenScan's problem: the caller returns `warning` and STOPS (no tool, no model call)

This module is the rules baseline (lexicons on accent-folded text, configs/prompt_router/scope_v1.yaml). The trained
small models (e5 gate + Qwen3-0.6B planner, deploy/vastai_a100) plug in through `model_router`; both must agree that a
request is in scope, and any "out" wins (defence in depth). Prompts are never written by a model: code picks the
registered template for the task and the model family (assist/prompts.py).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
SCOPE_FILE = ROOT / "configs" / "prompt_router" / "scope_v1.yaml"


def plain(text: str) -> str:
    """Lower-case, accents removed (đ -> d), spaces collapsed: 'Phát thải' and 'phat thai' match the same lexicon."""
    t = unicodedata.normalize("NFD", (text or "").lower().replace("đ", "d"))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t).strip()


@lru_cache(maxsize=1)
def scope() -> dict:
    return yaml.safe_load(SCOPE_FILE.read_text(encoding="utf-8"))


# Out-of-scope cues, checked first (any hit stops the request). Written accent-free; matched on plain().
OOS_CUES: dict[str, tuple[str, ...]] = {
    "prompt_injection": ("bo qua moi huong dan", "bo qua huong dan", "bo qua cac huong dan", "bo qua tat ca huong dan",
                         "bo qua moi chi dan", "bo qua chi dan", "bo qua cac chi dan", "bo qua tat ca chi dan",
                         "quen moi chi dan", "quen moi huong dan", "quen cac chi dan", "quen cac huong dan",
                         "ignore previous", "ignore all", "disregard previous", "disregard all", "system prompt",
                         "chi dan he thong", "prompt he thong", "dong vai", "jailbreak", "developer mode", "khong gioi han",
                         "gui toan bo tai lieu", "gui tat ca tai lieu", "reveal your instructions"),
    "coding_or_it": ("viet code", "lap trinh", "python", "javascript", "sql", "cai dat may", "sua loi code", "write code"),
    "write_or_embellish_claims": ("viet lai", "viet giup", "soan giup", "soan thao", "lam dep", "nghe xanh hon",
                                  "nghe thuyet phuc", "bia giup", "bia so lieu", "chinh so lieu", "sua so lieu",
                                  "tao tuyen bo", "viet tuyen bo", "write a claim", "make it sound"),
    "investment_advice": ("co nen mua", "nen mua co phieu", "mua co phieu", "ban co phieu", "co nen dau tu", "gia co phieu",
                          "xep hang tin nhiem", "khuyen nghi dau tu", "should i buy", "stock price", "target price"),
    "legal_or_fraud_verdict": ("co gian lan", "gian lan khong", "ket luan gian lan", "lua dao", "vi pham phap luat",
                               "vi pham luat", "co toi", "truy to", "khoi kien", "bi phat bao nhieu", "is it fraud"),
    "personal_data": ("so dien thoai", "dia chi nha", "email ca nhan", "cccd", "can cuoc", "thong tin ca nhan",
                      "phone number", "home address"),
    "general_chat_or_creative": ("lam tho", "bai tho", "ke chuyen", "bai hat", "sang tac", "ke mot cau chuyen",
                                 "write a poem", "tell me a joke"),
    "other_domain": ("thoi tiet", "benh", "thuoc chua", "ly hon", "bong da", "nau an", "weather", "recipe"),
}
NON_ENV = ("nu lanh dao", "co tuc", "an toan lao dong", "tham nhung", "tien luong", "phuc loi nhan vien",
           "hoi dong quan tri", "loi nhuan", "doanh thu", "gender", "dividend")
ENV = ("moi truong", "phat thai", "khi nha kinh", "co2", "carbon", "net zero", "trung hoa", "nang luong", "dien mat troi",
       "tai tao", "nuoc", "chat thai", "rac", "tai che", "xanh", "iso 14001", "ptbv", "phat trien ben vung",
       "ben vung", "esg", "tuyen bo", "bao cao thuong nien", "dam bao doc lap", "isae", "issa", "greenwash",
       "tay xanh", "emission", "renewable", "waste", "water", "sustainability", "khi thai", "nhua", "rung", "tieu thu dien")
TASK_CUES: dict[str, tuple[str, ...]] = {
    "verify_claim": ("kiem tra", "xac minh", "doi chieu", "dung khong", "co dung", "co that", "co bang chung",
                     "verify", "check", "fact check", "chung minh"),
    "extract_claims": ("liet ke", "tim cac tuyen bo", "trich", "co nhung tuyen bo", "tong hop cac tuyen bo", "list"),
    "check_attributes": ("thieu", "chi so", "ky bao cao", "nam goc", "pham vi", "da neu", "missing"),
    "explain_verdict": ("giai thich", "vi sao", "tai sao", "ly do", "explain", "why"),
    "find_evidence": ("bang chung", "trang nao", "doan nao", "nguon", "evidence", "o dau trong"),
    "review_assurance": ("dam bao doc lap", "to dam bao", "isae", "issa", "bao cao dam bao", "assurance", "kiem toan doc lap"),
    "assess_report_risk": ("rui ro", "tay xanh", "uu tien soat", "danh gia toan bo", "ca bo ho so", "greenwashing risk"),
    # Background-knowledge questions (D-2026-11-14-02): answered by the domain_lookup tool, no run needed.
    "explain_concept": ("la gi", "nghia la", "khai niem", "dinh nghia", "cach tinh", "cong thuc", "tinh nhu the nao",
                        "tinh the nao", "dau hieu", "khac gi", "khac nhau", "the nao la", "claim chuan", "tuyen bo chuan",
                        "can nhung gi", "nhu the nao moi", "van de gi", "thi sao", "co phai tay xanh",
                        "what is", "how to calculate", "difference between"),
}
# Domain terms that make a request environmental even without ENV words ("Scope 2 theo thị trường là gì?"), and that turn
# a claim-less "giải thích ..." / "... thiếu gì" into a background-knowledge question instead of asking for a claim.
DOMAIN_TERMS = ("scope 1", "scope 2", "scope 3", "pham vi 1", "pham vi 2", "pham vi 3", "nam goc", "base year",
                "cuong do phat thai", "tin chi carbon", "tin chi", "offset", "i-rec", "location-based", "market-based",
                "theo vi tri", "theo thi truong", "net zero", "trung hoa carbon", "dam bao han che", "dam bao hop ly",
                "limited assurance", "reasonable assurance", "trai phieu xanh", "tin dung xanh", "phan loai xanh",
                "kiem ke khi nha kinh", "ghg protocol", "iso 14064", "iso 14068", "sbti", "nhan sinh thai", "ranh gioi to chuc")
CONCEPT_ONLY_TASKS = {"explain_verdict", "check_attributes"}
# Short tickers that are also Vietnamese words ("tra" in "kiểm tra", "pan", "sab", "pow") are left out on purpose.
COMPANIES = ("hoa phat", "hpg", "vinamilk", "vnm", "sabeco", "pnj", "bao viet", "bvh", "traphaco", "coteccons",
             "ctd", "pv power", "vinh hoan", "vhc", "masan", "msn", "fpt", "novaland", "nvl", "acb", "vpbank",
             "vpb", "dam ca mau", "dcm", "pvcfc", "vingroup", "hoa sen", "hsg", "duoc hau giang", "dhg", "pan group",
             "dong phu", "dpr", "gemadept", "gmd", "petrolimex", "plx", "vietjet", "vjc")
NEEDS = {"verify_claim": "claim", "check_attributes": "claim", "explain_verdict": "claim", "find_evidence": "claim"}


@dataclass
class Route:
    status: str
    category: str | None = None
    warning: str | None = None
    tasks: list[str] = field(default_factory=list)
    slots: dict = field(default_factory=dict)
    source: str = "rules"

    @property
    def stop(self) -> bool:
        return self.status != "ok"


def _has(p: str, cues) -> bool:
    return any(re.search(rf"(?<![a-z0-9]){re.escape(c)}(?![a-z0-9])", p) for c in cues)


def _slots(request: str) -> dict:
    claim = None
    m = re.search(r"[\"“«]([^\"”»]{12,})[\"”»]", request)
    if m:
        claim = m.group(1).strip()
    else:
        m = re.search(r":\s*(.{20,})$", request.strip(), flags=re.S)
        if m:
            claim = m.group(1).strip()
    year = re.search(r"\b(20[0-3]\d)\b", request)
    p = plain(request)
    company = next((c for c in COMPANIES if re.search(rf"(?<![a-z0-9]){re.escape(c)}(?![a-z0-9])", p)), None)
    return {"claim": claim, "company": company, "year": int(year.group(1)) if year else None}


ARG_CATEGORIES = ("prompt_injection", "write_or_embellish_claims", "personal_data")


def arg_guard(text: str) -> str | None:
    """For a tool argument that is data (a claim, an assurance statement): only the dangerous categories stop it."""
    p = plain(text)
    return next((c for c in ARG_CATEGORIES if _has(p, OOS_CUES[c])), None)


def rules_route(request: str) -> Route:
    s = scope()
    p = plain(request)
    outside = plain(re.sub(r"[\"“«][^\"”»]*[\"”»]", " ", request))   # a quoted claim is data, not the request
    for cat, cues in OOS_CUES.items():
        if _has(p if cat == "prompt_injection" else outside, cues):
            return Route("out_of_scope", cat, f"{s['warning_prefix']} {s['out_of_scope'][cat]}")
    domain = _has(p, DOMAIN_TERMS)
    env = _has(p, ENV) or domain
    if _has(p, NON_ENV) and not env:
        return Route("out_of_scope", "non_environmental", f"{s['warning_prefix']} {s['out_of_scope']['non_environmental']}")
    tasks = [t for t, cues in TASK_CUES.items() if _has(p, cues)]
    if not env:
        return Route("out_of_scope", "other_domain", f"{s['warning_prefix']} {s['out_of_scope']['other_domain']}")
    slots = _slots(request)
    if not slots["claim"] and (domain and set(tasks) <= CONCEPT_ONLY_TASKS or "explain_concept" in tasks):
        # A question about the domain, not about a claim: answer from background knowledge instead of asking for one.
        tasks = [t for t in tasks if t not in NEEDS] + (["explain_concept"] if "explain_concept" not in tasks else [])
    if not tasks:
        tasks = ["verify_claim"] if slots["claim"] else ["assess_report_risk"]
    missing = sorted({NEEDS[t] for t in tasks if t in NEEDS and not slots.get(NEEDS[t])})
    ask = s["need_info"].format(missing="câu tuyên bố cần xét (chép trong ngoặc kép)")
    runnable = [t for t in tasks if t not in NEEDS or slots.get(NEEDS[t])]
    if missing and not runnable:
        return Route("need_info", None, ask, tasks, slots)
    # Some tasks can run without the claim (a list, the queue): run those and say what the rest needs.
    return Route("ok", None, ask if missing else None, tasks, slots)


def route(request: str, model_router=None) -> Route:
    """Rules, then the trained router when given. Any 'out_of_scope' wins; 'need_info' beats 'ok'."""
    r = rules_route(request)
    if model_router is None or r.status == "out_of_scope":
        return r
    m = model_router(request)
    if m.status == "out_of_scope":
        return m
    if m.status == "need_info" or r.status == "need_info":
        return m if m.status == "need_info" else r
    return Route("ok", None, None, sorted(set(m.tasks) | set(r.tasks)), {**r.slots, **{k: v for k, v in m.slots.items() if v}},
                 "rules+model")
