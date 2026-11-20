"""Uploaded org packs (org-pack-v1): send, check, approve by someone else, choose per run.

`org_pack.py` decides what a pack means; this module decides how a pack an
organisation sends over the API becomes one a run may use:

1. **Upload.** A zip (or pack.yaml plus its documents) is unpacked with limits
   (size, file count, allowed types, no absolute or `..` paths), validated by
   `load_org_pack`, and stored under `.quantum/org_packs/<org_id>/<version>/`.
   A refused pack is not stored; the answer lists every problem.
2. **Always a draft on arrival.** `approved_by` / `approved_at` in an uploaded
   file are cleared, so nobody can approve their own upload by typing a name.
   A draft is loaded and shown, and its rules are NOT_APPLICABLE.
3. **Four-eyes approval.** `approve` writes the approver into the stored copy
   and re-validates it; the approver must differ from the uploader.
4. **Per-run choice.** `resolve(["ngan_hang_abc", "kiem_toan_x@0.2.0-1a2b3c4d5e"])`
   gives the folders for one analysis: an org id means its latest approved
   version, `org@version` a specific stored version. Retired versions cannot be chosen.

Every step is appended to `registry.jsonl`, which is the audit trail: nothing
in it is edited, a later event supersedes an earlier one.
"""

from __future__ import annotations

import io
import os
import re
import shutil
import tempfile
import zipfile
from datetime import UTC, date, datetime
from pathlib import Path, PurePosixPath

import yaml

from quantum_gw.utils.jsonl import dumps, read_jsonl

from .org_pack import OrgPackError, load_org_pack

ALLOWED_SUFFIXES = {".yaml", ".yml", ".md", ".txt", ".pdf", ".docx"}
MAX_FILES = 30
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 5 * 1024 * 1024
_ORG_ID = re.compile(r"^[a-z0-9_]+$")


class UploadError(ValueError):
    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("; ".join(problems))


def store_dir() -> Path:
    return Path(os.environ.get("QUANTUM_ORG_PACK_STORE", ".quantum/org_packs"))


def _registry_file() -> Path:
    return store_dir() / "registry.jsonl"


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _append(event: dict) -> dict:
    path = _registry_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(dumps(event) + "\n")
    return event


def _safe_path(name: str) -> str:
    """A relative POSIX path inside the pack, or UploadError."""
    raw = (name or "").replace("\\", "/")
    path = PurePosixPath(raw)
    if not raw or path.is_absolute() or re.match(r"^[A-Za-z]:", raw) or ".." in path.parts:
        raise UploadError([f"đường dẫn không an toàn trong gói tải lên: `{name}`."])
    return str(path)


def _collect(files: list[tuple[str, bytes]]) -> dict[str, bytes]:
    entries: dict[str, bytes] = {}
    if len(files) == 1 and files[0][0].lower().endswith(".zip"):
        try:
            archive = zipfile.ZipFile(io.BytesIO(files[0][1]))
        except zipfile.BadZipFile as exc:
            raise UploadError(["tệp .zip hỏng hoặc không phải zip."]) from exc
        infos = [i for i in archive.infolist() if not i.is_dir()]
        if len(infos) > MAX_FILES:
            raise UploadError([f"gói có {len(infos)} tệp, tối đa {MAX_FILES}."])
        if sum(i.file_size for i in infos) > MAX_TOTAL_BYTES:
            raise UploadError([f"gói giải nén quá {MAX_TOTAL_BYTES // (1024 * 1024)} MB."])
        for info in infos:
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise UploadError([f"`{info.filename}` là liên kết tượng trưng; không nhận."])
            if info.file_size > MAX_FILE_BYTES:
                raise UploadError([f"`{info.filename}` quá {MAX_FILE_BYTES // (1024 * 1024)} MB."])
            entries[_safe_path(info.filename)] = archive.read(info)
    else:
        if len(files) > MAX_FILES:
            raise UploadError([f"gửi {len(files)} tệp, tối đa {MAX_FILES}."])
        for name, content in files:
            if len(content) > MAX_FILE_BYTES:
                raise UploadError([f"`{name}` quá {MAX_FILE_BYTES // (1024 * 1024)} MB."])
            entries[PurePosixPath(_safe_path(name)).name] = content
    if sum(len(v) for v in entries.values()) > MAX_TOTAL_BYTES:
        raise UploadError([f"tổng dung lượng quá {MAX_TOTAL_BYTES // (1024 * 1024)} MB."])
    # A zip of the folder itself ("ngan_hang_abc/pack.yaml"): drop the one top folder.
    tops = {PurePosixPath(k).parts[0] for k in entries}
    if "pack.yaml" not in entries and len(tops) == 1 and all(len(PurePosixPath(k).parts) > 1 for k in entries):
        top = tops.pop()
        entries = {str(PurePosixPath(*PurePosixPath(k).parts[1:])): v for k, v in entries.items()}
        if not entries:
            raise UploadError([f"thư mục `{top}` rỗng."])
    if "pack.yaml" not in entries:
        raise UploadError(["không có `pack.yaml` ở gốc gói."])
    bad = sorted(k for k in entries if PurePosixPath(k).suffix.lower() not in ALLOWED_SUFFIXES)
    if bad:
        raise UploadError([f"loại tệp không nhận: {', '.join(bad)} (chỉ {', '.join(sorted(ALLOWED_SUFFIXES))})."])
    return entries


def _dump(data: dict) -> str:
    return ("# Bản lưu do GreenScan ghi lại khi tải lên (org-pack-v1); chú thích của tệp gốc không được giữ.\n"
            + yaml.safe_dump(data, allow_unicode=True, sort_keys=False))


def ingest(files: list[tuple[str, bytes]], uploaded_by: str, note: str = "") -> dict:
    """Validate and store an uploaded pack as a draft. Never raises for a bad pack: the answer says why."""
    uploaded_by = (uploaded_by or "").strip()
    if not uploaded_by:
        return {"status": "rejected", "errors": ["cần tên người tải lên (vết kiểm toán)."]}
    try:
        entries = _collect(files)
    except UploadError as exc:
        return {"status": "rejected", "errors": exc.problems}
    try:
        data = yaml.safe_load(entries["pack.yaml"].decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        return {"status": "rejected", "errors": [f"`pack.yaml` không phải YAML UTF-8 hợp lệ: {exc}"]}
    if not isinstance(data, dict) or not _ORG_ID.match(str(data.get("org_id") or "")):
        return {"status": "rejected", "errors": ["`org_id` thiếu hoặc không hợp lệ (chữ thường không dấu, số, _)."]}
    org_id = str(data["org_id"])
    self_approved = bool(str(data.get("approved_by") or "").strip())
    data["approved_by"], data["approved_at"] = "", ""
    with tempfile.TemporaryDirectory(prefix="org-upload-") as tmp:
        folder = Path(tmp) / org_id
        for name, content in entries.items():
            target = folder / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        (folder / "pack.yaml").write_text(_dump(data), encoding="utf-8")
        try:
            pack = load_org_pack(folder)
        except OrgPackError as exc:
            return {"status": "rejected", "org_id": org_id, "errors": exc.problems}
        version = f"{pack.pack_version}-{pack.sha256[:10]}"
        dest = store_dir() / org_id / version / org_id
        if dest.exists():
            return {"status": "duplicate", "org_id": org_id, "version": version,
                    "errors": ["bản này đã được tải lên trước đó."]}
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(folder, dest)
    event = _append({
        "event": "uploaded", "org_id": org_id, "version": version, "pack_version": pack.pack_version,
        "org_name": pack.org_name, "n_rules": len(pack.rules), "sha256": pack.sha256,
        "path": str(dest).replace("\\", "/"), "by": uploaded_by, "at": _now(),
        "self_approval_removed": self_approved, "note": note,
    })
    return {"status": "draft", **{k: event[k] for k in ("org_id", "version", "pack_version", "org_name", "n_rules",
                                                       "sha256", "path", "self_approval_removed")},
            "warnings": pack.warnings}


def state() -> dict[tuple[str, str], dict]:
    """The current state of every stored version, folded from the event log."""
    out: dict[tuple[str, str], dict] = {}
    for event in read_jsonl(_registry_file()):
        key = (event["org_id"], event["version"])
        if event["event"] == "uploaded":
            out[key] = {k: event.get(k) for k in ("org_id", "version", "pack_version", "org_name", "n_rules",
                                                  "sha256", "path", "self_approval_removed")}
            out[key].update(status="draft", uploaded_by=event["by"], uploaded_at=event["at"],
                            approved_by="", approved_at="")
        elif key in out and event["event"] == "approved":
            out[key].update(status="approved", approved_by=event["by"], approved_at=event["at"],
                            sha256=event.get("sha256", out[key]["sha256"]))
        elif key in out and event["event"] == "retired":
            out[key].update(status="retired", retired_by=event["by"], retired_at=event["at"])
    return out


def list_packs() -> list[dict]:
    return sorted(state().values(), key=lambda e: (e["org_id"], e["uploaded_at"]))


def _get(org_id: str, version: str) -> dict:
    entry = state().get((org_id, version))
    if entry is None:
        raise ValueError(f"không có pack `{org_id}` phiên bản `{version}` trong kho tải lên.")
    return entry


def approve(org_id: str, version: str, approved_by: str, comment: str = "") -> dict:
    entry = _get(org_id, version)
    approved_by = (approved_by or "").strip()
    if not approved_by:
        raise ValueError("cần tên người duyệt.")
    if entry["status"] != "draft":
        raise ValueError(f"pack đang ở trạng thái `{entry['status']}`, chỉ duyệt được bản nháp.")
    if approved_by.casefold() == (entry["uploaded_by"] or "").casefold():
        raise ValueError("người duyệt phải khác người tải lên (bốn mắt).")
    file = Path(entry["path"]) / "pack.yaml"
    data = yaml.safe_load(file.read_text(encoding="utf-8"))
    data["approved_by"], data["approved_at"] = approved_by, date.today().isoformat()
    file.write_text(_dump(data), encoding="utf-8")
    try:
        pack = load_org_pack(file.parent)
    except OrgPackError as exc:  # cannot happen for a pack that validated as a draft, but never half-approve
        data["approved_by"], data["approved_at"] = "", ""
        file.write_text(_dump(data), encoding="utf-8")
        raise ValueError("pack không còn hợp lệ: " + "; ".join(exc.problems)) from exc
    _append({"event": "approved", "org_id": org_id, "version": version, "by": approved_by, "at": _now(),
             "sha256": pack.sha256, "comment": (comment or "").strip()})
    return _get(org_id, version)


def retire(org_id: str, version: str, by: str, comment: str = "") -> dict:
    entry = _get(org_id, version)
    if not (by or "").strip():
        raise ValueError("cần tên người thu hồi.")
    if entry["status"] == "retired":
        return entry
    _append({"event": "retired", "org_id": org_id, "version": version, "by": by.strip(), "at": _now(),
             "comment": (comment or "").strip()})
    return _get(org_id, version)


def resolve(selectors: list[str]) -> list[str]:
    """Folders for the packs one run should use. Raises ValueError naming an unknown or retired selector."""
    current = state()
    paths = []
    for selector in [s.strip() for s in selectors if s and s.strip()]:
        org_id, _, version = selector.partition("@")
        if version:
            entry = current.get((org_id, version))
            if entry is None or entry["status"] == "retired":
                raise ValueError(f"`{selector}`: không có hoặc đã thu hồi.")
        else:
            approved = [e for e in current.values() if e["org_id"] == org_id and e["status"] == "approved"]
            if not approved:
                raise ValueError(f"`{org_id}`: chưa có phiên bản nào được duyệt; chọn `{org_id}@<phiên bản>` để xem bản nháp.")
            entry = max(approved, key=lambda e: e["approved_at"])
        paths.append(entry["path"])
    return paths
