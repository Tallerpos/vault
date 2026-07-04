#!/usr/bin/env python3
import sys
import os
import json
import re
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
from tag_manager import TagManager
from yaml_updater import YAMLUpdater
from api_client import DeepSeekClient

CONFIG_PATH = Path(__file__).parent / "config.json"
LOG_DIR = Path(__file__).parent / "logs"
HASH_DIR = Path(__file__).parent / "cache" / "hashes"

class NoteClassifier:
    def __init__(self):
        with open(CONFIG_PATH) as f:
            self.config = json.load(f)
        LOG_DIR.mkdir(exist_ok=True)
        HASH_DIR.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=LOG_DIR / "classifier.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)
        self.tag_manager = TagManager(self.config["tag_registry"]["path"], self.config["tag_registry"]["aliases"])
        self.api_client = DeepSeekClient(self.config["api"])
        self.yaml_updater = YAMLUpdater(prefix=self.config["classification"]["prefix"])

    def _extract_body(self, content: str) -> str:
        body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, count=1, flags=re.DOTALL)
        ai_lines = [l for l in body.split("\n") if not l.startswith("ai_")]
        return "\n".join(ai_lines).strip()

    def _content_changed_significantly(self, old_body: str, new_body: str, threshold: float = 0.5) -> bool:
        if not old_body and new_body:
            return True
        if old_body and not new_body:
            return True
        if old_body == new_body:
            return False
        old_words = set(old_body.lower().split())
        new_words = set(new_body.lower().split())
        if not old_words and not new_words:
            return False
        intersection = old_words & new_words
        union = old_words | new_words
        similarity = len(intersection) / len(union) if union else 1.0
        return (1 - similarity) > threshold

    def get_file_hash(self, file_path: Path) -> str:
        content = file_path.read_text(encoding="utf-8")
        return hashlib.sha256(content.encode()).hexdigest()

    def was_classified(self, content: str) -> bool:
        return "ai_classified_at" in content

    def classify_note(self, file_path: Path) -> dict:
        try:
            content = file_path.read_text(encoding="utf-8")
            already_classified = self.was_classified(content)

            if already_classified:
                cached_hash_file = HASH_DIR / (file_path.name + ".body")
                current_body = self._extract_body(content)
                if cached_hash_file.exists():
                    old_body = cached_hash_file.read_text(encoding="utf-8")
                    if not self._content_changed_significantly(old_body, current_body):
                        return {"status": "skipped", "reason": "already classified, no significant change"}

            tag_context = self.tag_manager.get_tag_context()
            system_prompt = self.config.get("system_prompt", "").format(
                existing_tags=json.dumps(tag_context["tags"], ensure_ascii=False),
                existing_categories=json.dumps(tag_context["categories"], indent=2, ensure_ascii=False)
            )
            user_prompt = f"Clasifica esta nota. USA SOLO tags existentes cuando sea posible.\n\nCONTENIDO:\n{content[:4000]}\n\nResponde con JSON."
            classification = self.api_client.classify(system_prompt, user_prompt)
            normalized_tags = [self.tag_manager.normalize_tag(t) for t in classification.get("tags", [])]
            normalized_tags = list(dict.fromkeys(normalized_tags))[:5]
            ai_fields = {
                "tags": normalized_tags,
                "category": classification.get("category", "miscelanea"),
                "summary": classification.get("summary", ""),
                "importance": classification.get("importance", 3),
                "key_topics": classification.get("key_topics", []),
                "classified_at": datetime.now(timezone.utc).isoformat()
            }
            updated_content = self.yaml_updater.update_frontmatter(content, ai_fields)
            file_path.write_text(updated_content, encoding="utf-8")

            body_cache = HASH_DIR / (file_path.name + ".body")
            body_cache.write_text(self._extract_body(updated_content), encoding="utf-8")

            self.tag_manager.register_tags(normalized_tags, classification.get("category"))
            action = "reclassified" if already_classified else "classified"
            return {"status": "success", "action": action, "tags": normalized_tags}
        except Exception as e:
            self.logger.error(f"Classification failed for {file_path}: {e}")
            return {"status": "error", "error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: classifier.py <file_path>")
        sys.exit(1)
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    classifier = NoteClassifier()
    result = classifier.classify_note(file_path)
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result["status"] in ["success", "skipped"] else 1)

if __name__ == "__main__":
    main()
