from pathlib import Path
import yaml
from .models import Registry, CompanyConfig

def load_companies(path: Path, include_disabled: bool=False) -> list[CompanyConfig]:
    raw=yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    items=Registry.model_validate(raw).companies
    return items if include_disabled else [x for x in items if x.enabled]
