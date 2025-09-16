from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict
from .config import CFG

DEFAULT_PROFILE = {
    "learning_style": "visual",
    "level": "intermedio",
    "language": "es",
    "constraints": {"max_words": CFG.max_words},
}

def load_profile(user_id: str, profiles_dir: Path = CFG.profiles_path) -> Dict[str, Any]:
    path = profiles_dir / f"{user_id}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_PROFILE
