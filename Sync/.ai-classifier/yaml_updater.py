#!/usr/bin/env python3
import re
import json
from datetime import datetime

class YAMLUpdater:
    def __init__(self, prefix: str = "ai_", fields: dict = None):
        self.prefix = prefix
        self.fields = fields or {}

    def parse_frontmatter(self, content: str) -> dict:
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            try:
                result = {}
                current_key = None
                current_value = []
                in_list = False
                for line in match.group(1).split('\n'):
                    if re.match(r'^[a-zA-Z_]+:', line):
                        if current_key:
                            result[current_key] = self._parse_value('\n'.join(current_value))
                        current_key = line.split(':')[0].strip()
                        current_value = [line.split(':', 1)[1].strip()] if ':' in line else []
                        in_list = False
                    elif line.strip().startswith('-'):
                        in_list = True
                        current_value.append(line.strip().lstrip('- ').strip())
                    elif line.strip():
                        current_value.append(line.strip())
                if current_key:
                    result[current_key] = self._parse_value('\n'.join(current_value))
                return result
            except Exception:
                return {}
        return {}

    def _parse_value(self, value: str) -> any:
        if not value:
            return ""
        if value.startswith('[') and value.endswith(']'):
            try:
                return json.loads(value)
            except:
                return [v.strip().strip('"') for v in value[1:-1].split(',') if v.strip()]
        return value.strip('"')

    def update_frontmatter(self, content: str, ai_fields: dict) -> str:
        existing = self.parse_frontmatter(content)
        for key, value in ai_fields.items():
            existing[self.prefix + key] = value
        fm_lines = []
        for key, value in existing.items():
            if isinstance(value, list):
                fm_lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
            else:
                fm_lines.append(f"{key}: {value}")
        content_without_fm = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, count=1, flags=re.DOTALL)
        return '---\n' + '\n'.join(fm_lines) + '\n---\n' + content_without_fm

    def strip_ai_fields(self, content: str) -> str:
        existing = self.parse_frontmatter(content)
        cleaned = {k: v for k, v in existing.items() if not k.startswith(self.prefix)}
        fm_lines = []
        for key, value in cleaned.items():
            if isinstance(value, list):
                fm_lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
            else:
                fm_lines.append(f"{key}: {value}")
        content_without_fm = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, count=1, flags=re.DOTALL)
        return '---\n' + '\n'.join(fm_lines) + '\n---\n' + content_without_fm
