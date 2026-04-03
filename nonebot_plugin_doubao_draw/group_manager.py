import os
import json
from typing import List

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
DISABLED_FILE = os.path.join(DATA_DIR, "draw_disabled_groups.json")

class GroupManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._disabled_groups: List[int] = []
        self._load()

    def _load(self):
        if os.path.exists(DISABLED_FILE):
            try:
                with open(DISABLED_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._disabled_groups = data.get("disabled_groups", [])
            except Exception:
                self._disabled_groups = []

    def _save(self):
        with open(DISABLED_FILE, "w", encoding="utf-8") as f:
            json.dump({"disabled_groups": self._disabled_groups}, f, ensure_ascii=False, indent=2)

    def is_disabled(self, group_id: int) -> bool:
        return group_id in self._disabled_groups

    def disable(self, group_id: int) -> bool:
        if group_id in self._disabled_groups:
            return False
        self._disabled_groups.append(group_id)
        self._save()
        return True

    def enable(self, group_id: int) -> bool:
        if group_id not in self._disabled_groups:
            return False
        self._disabled_groups.remove(group_id)
        self._save()
        return True

    def get_disabled_groups(self) -> List[int]:
        return self._disabled_groups.copy()

_manager = None

def get_group_manager() -> GroupManager:
    global _manager
    if _manager is None:
        _manager = GroupManager()
    return _manager
