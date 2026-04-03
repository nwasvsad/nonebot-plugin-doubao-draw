import os
import json
from typing import Optional, Dict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
PROMPT_FILE = os.path.join(DATA_DIR, "draw_prompts.json")

class PromptStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._prompts: Dict[str, str] = {}
        self._load()

    def _load(self):
        if os.path.exists(PROMPT_FILE):
            try:
                with open(PROMPT_FILE, "r", encoding="utf-8") as f:
                    self._prompts = json.load(f)
            except Exception:
                self._prompts = {}

    def _save(self):
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            json.dump(self._prompts, f, ensure_ascii=False, indent=2)

    def get_all(self) -> Dict[str, str]:
        return self._prompts.copy()

    def get(self, key: str) -> Optional[str]:
        return self._prompts.get(key)

    def add(self, key: str, value: str) -> bool:
        if key in self._prompts:
            return False
        self._prompts[key] = value
        self._save()
        return True

    def delete(self, key: str) -> bool:
        if key not in self._prompts:
            return False
        del self._prompts[key]
        self._save()
        return True

    def exists(self, key: str) -> bool:
        return key in self._prompts

_store = None

def get_prompt_store() -> PromptStore:
    global _store
    if _store is None:
        _store = PromptStore()
    return _store
