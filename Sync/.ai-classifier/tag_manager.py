#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

class TagManager:
    def __init__(self, registry_path: str, aliases: dict):
        self.registry_path = Path(registry_path)
        self.aliases = aliases
        self.registry = self._load_registry()

    def _load_registry(self) -> dict:
        if self.registry_path.exists():
            with open(self.registry_path) as f:
                return json.load(f)
        return {"version": "1.0", "last_updated": "", "tags": {}, "categories": {}}

    def _save_registry(self):
        self.registry["last_updated"] = datetime.utcnow().isoformat() + "Z"
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)

    def get_tag_context(self) -> dict:
        return {"tags": list(self.registry["tags"].keys()), "categories": self.registry.get("categories", {}), "total_tags": len(self.registry["tags"])}

    def normalize_tag(self, tag: str) -> str:
        return self.aliases.get(tag.lower().strip(), tag.lower().strip())

    def register_tags(self, tags: list, category: str = None):
        updated = False
        for tag in tags:
            if tag not in self.registry["tags"]:
                self.registry["tags"][tag] = {"count": 0, "first_seen": datetime.utcnow().isoformat() + "Z", "category": category or "uncategorized"}
                updated = True
            self.registry["tags"][tag]["count"] += 1
        if updated:
            self._save_registry()

    def tag_exists(self, tag: str) -> bool:
        return tag in self.registry["tags"]
