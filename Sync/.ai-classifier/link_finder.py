#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path

VAULT_ROOT = Path('/opt/vault/Sync')

class LinkFinder:
    def __init__(self, tag_registry_path, config=None):
        self.config = config or {}
        self.min_score = self.config.get('min_score', 0.35)
        self.max_links = self.config.get('max_links', 5)
        self.registry = self._load_registry(tag_registry_path)
        self.notes_index = self._index_notes()

    def _load_registry(self, path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return {'tags': {}, 'co_occurrence': {}}

    def _index_notes(self):
        index = {}
        for md in VAULT_ROOT.rglob('*.md'):
            if any(part.startswith('.') or part == 'Templates' for part in md.parts):
                continue
            if not md.is_file():
                continue
            try:
                content = md.read_text(encoding='utf-8')
                fm = self._parse_frontmatter(content)
                if not fm:
                    continue
                rel = str(md.relative_to(VAULT_ROOT))
                index[rel] = {
                    'path': md,
                    'relative': rel,
                    'tags': fm.get('ai_tags', []),
                    'category': fm.get('ai_category', ''),
                    'key_topics': fm.get('ai_key_topics', []),
                    'title': fm.get('title', md.stem),
                }
            except Exception:
                continue
        return index

    def _parse_frontmatter(self, content):
        m = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not m:
            return {}
        try:
            import yaml
            return yaml.safe_load(m.group(1)) or {}
        except Exception:
            return {}

    def _jaccard(self, set_a, set_b):
        if not set_a and not set_b:
            return 0.0
        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union) if union else 0.0

    def _co_occurrence_boost(self, tags_a, tags_b):
        co = self.registry.get('co_occurrence', {})
        boost = 0.0
        pairs_checked = 0
        for t1 in tags_a:
            for t2 in tags_b:
                if t1 == t2:
                    continue
                k = f'{tuple(sorted([t1, t2]))[0]}__{tuple(sorted([t1, t2]))[1]}'
                count = co.get(k, 0)
                if count > 0:
                    boost += min(count / 10.0, 1.0)
                    pairs_checked += 1
        return boost / max(pairs_checked, 1)

    def _topic_overlap(self, topics_a, topics_b):
        if not topics_a or not topics_b:
            return 0.0
        set_a = set(t.lower().strip() for t in topics_a)
        set_b = set(t.lower().strip() for t in topics_b)
        return self._jaccard(set_a, set_b)

    def find_related(self, current_path, tags, category, key_topics):
        current = Path(current_path)
        candidates = []

        for rel, note in self.notes_index.items():
            note_path = note['path']
            if note_path == current:
                continue
            if not note_path.exists():
                continue

            tags_a = set(t.lower() for t in tags)
            tags_b = set(t.lower() for t in note['tags'])
            jaccard = self._jaccard(tags_a, tags_b)

            if jaccard == 0 and not (tags_a & tags_b):
                continue

            co_boost = self._co_occurrence_boost(tags, note['tags'])
            topic_score = self._topic_overlap(key_topics, note.get('key_topics', []))
            cat_bonus = 0.1 if category and note.get('category') == category else 0.0

            combined = (0.40 * jaccard) + (0.30 * co_boost) + (0.20 * topic_score) + (0.10 * cat_bonus)

            if combined >= self.min_score:
                candidates.append({
                    'path': note_path,
                    'relative': rel,
                    'score': round(combined, 3),
                    'shared_tags': list(tags_a & tags_b),
                })

        candidates.sort(key=lambda x: -x['score'])
        return candidates[:self.max_links]

    def build_wikilink(self, note_path, all_filenames=None):
        name = note_path.stem
        if all_filenames and len(all_filenames.get(name, [])) > 1:
            rel_dir = str(note_path.parent.relative_to(VAULT_ROOT))
            if rel_dir and rel_dir != '.':
                name = f'{rel_dir}/{name}'
        return f'[[{name}]]'

    def build_body_links(self, related):
        if not related:
            return ''
        links = []
        all_names = {}
        for r in related:
            n = r['path'].stem
            all_names.setdefault(n, []).append(r['path'])
        for r in related:
            links.append(self.build_wikilink(r['path'], all_names))
        return '\n\n---\n\n**Notas relacionadas:** ' + ' · '.join(links) + '\n'

    def inject_related(self, content, related):
        if not related:
            return content
        links = []
        all_names = {}
        for r in related:
            n = r['path'].stem
            all_names.setdefault(n, []).append(r['path'])
        for r in related:
            links.append(self.build_wikilink(r['path'], all_names))

        existing = self._parse_frontmatter(content)
        existing_related = existing.get('ai_related', [])
        existing_set = set(existing_related)
        new_links = [l for l in links if l not in existing_set]
        if not new_links:
            return content
        all_related = existing_related + new_links

        body_links = self.build_body_links(related)

        m = re.search(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
        if m:
            fm_content = m.group(0)
            body = content[m.end():]
            if body_links.strip() in body:
                return content
            return fm_content.rstrip('\n') + f'\nai_related: {json.dumps(all_related, ensure_ascii=False)}\n' + body.rstrip('\n') + '\n' + body_links
        else:
            fm = f'---\nai_related: {json.dumps(all_related, ensure_ascii=False)}\n---\n'
            return fm + content.rstrip('\n') + '\n' + body_links
