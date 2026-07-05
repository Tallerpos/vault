#!/usr/bin/env python3
import re, yaml

class YAMLUpdater:
    def __init__(self, prefix='ai_', fields=None):
        self.prefix = prefix

    def parse_frontmatter(self, content):
        m = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not m: return {}
        try: return yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError: return {}

    def update_frontmatter(self, content, ai_fields):
        fm = self.parse_frontmatter(content)
        m = re.match(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
        body = content[m.end():] if m else content
        for k, v in ai_fields.items():
            fm[self.prefix + k] = v
        return f'---\n{yaml.dump(fm, default_flow_style=None, allow_unicode=True, sort_keys=False, width=120, indent=2).strip()}\n---\n{body}'
