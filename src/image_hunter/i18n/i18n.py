from __future__ import annotations
import json, importlib.resources as pkg
from typing import Dict

_current: Dict[str, str] = {}
_fallback: Dict[str, str] = {}

SUPPORTED = {
    "en": "English",
    "pt_BR": "Português (Brasil)",
    "es": "Español",
    "fr": "Français",
}

def load(lang: str = "en") -> None:
    """Load translation JSON. Falls back to English if missing."""
    global _current, _fallback
    with pkg.files(__package__).joinpath("en.json").open("r", encoding="utf-8") as f:
        _fallback = json.load(f)
    p = pkg.files(__package__).joinpath(f"{lang}.json")
    _current = _fallback if not p.is_file() else json.loads(p.read_text(encoding="utf-8"))

def t(key: str, **kwargs) -> str:
    s = _current.get(key, _fallback.get(key, key))
    return s.format(**kwargs) if kwargs else s
