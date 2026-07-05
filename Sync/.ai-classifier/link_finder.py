#!/usr/bin/env python3
"""Link Finder v3.0 — Smarter note relationships.

Finds related notes using:
- Tag Jaccard similarity (40%)
- Co-occurrence boost (30%)
- Key topic overlap (20%)
- Category bonus (10%)
- Temporal proximity bonus

Outputs Obsidian-native callout blocks instead of raw markdown.
"""
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

    def _is_useful_note(self, md, content, fm):
        """Filtra notas que no deberían ser targets de links."""
        name = md.stem.lower()
        # Nombres genéricos
        if name in ('sin título', 'untitled', 'sin titulo', 'config',
                     'sistema-ai', 'guia_recuperacion', 'enlaces'):
            return False
        # Notas de prueba
        if 'prueba' in name or 'test' in name:
            return False
        # Body demasiado corto
        body = content
        m = re.search(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
        if m:
            body = content[m.end():]
        # Limpiar secciones inyectadas
        body = re.sub(
            r'\n*> \[!abstract\][- ].*?(?=\n[^>]|\Z)',
            '', body, flags=re.DOTALL
        )
        body = re.sub(
            r'\n*---\n+\*\*Notas relacionadas:\*\*.*',
            '', body, flags=re.DOTALL
        )
        body = body.strip()
        if len(body) < 30:
            return False
        # Debe tener ai_tags para ser linkeable
        ai_tags = fm.get('ai_tags', [])
        if not ai_tags:
            return False
        return True

    def _index_notes(self):
        """Indexa todas las notas útiles del vault."""
        index = {}
        for md in VAULT_ROOT.rglob('*.md'):
            # Saltar directorios ocultos y Templates
            if any(part.startswith('.') or part == 'Templates'
                   for part in md.parts):
                continue
            if not md.is_file():
                continue
            try:
                content = md.read_text(encoding='utf-8')
                fm = self._parse_frontmatter(content)
                if not fm:
                    continue
                if not self._is_useful_note(md, content, fm):
                    continue
                rel = str(md.relative_to(VAULT_ROOT))
                index[rel] = {
                    'path': md,
                    'relative': rel,
                    'tags': fm.get('ai_tags', []) or [],
                    'category': fm.get('ai_category', ''),
                    'key_topics': fm.get('ai_key_topics', []) or [],
                    'title': fm.get('title', md.stem),
                    'fecha': str(fm.get('fecha', '')),
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
        """Similitud Jaccard entre dos conjuntos."""
        if not set_a and not set_b:
            return 0.0
        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union) if union else 0.0

    def _co_occurrence_boost(self, tags_a, tags_b):
        """Calcula boost por co-occurrence de tags."""
        co = self.registry.get('co_occurrence', {})
        boost = 0.0
        pairs_checked = 0
        for t1 in tags_a:
            for t2 in tags_b:
                if t1 == t2:
                    continue
                key = '__'.join(sorted([t1, t2]))
                count = co.get(key, 0)
                if count > 0:
                    boost += min(count / 10.0, 1.0)
                    pairs_checked += 1
        return boost / max(pairs_checked, 1)

    def _topic_overlap(self, topics_a, topics_b):
        """Overlap entre key_topics."""
        if not topics_a or not topics_b:
            return 0.0
        set_a = set(t.lower().strip() for t in topics_a)
        set_b = set(t.lower().strip() for t in topics_b)
        return self._jaccard(set_a, set_b)

    def _date_proximity(self, date_a, date_b):
        """Bonus por proximidad temporal (misma semana = bonus)."""
        if not date_a or not date_b:
            return 0.0
        try:
            from datetime import datetime
            da = datetime.strptime(str(date_a)[:10], '%Y-%m-%d')
            db = datetime.strptime(str(date_b)[:10], '%Y-%m-%d')
            diff = abs((da - db).days)
            if diff <= 1:
                return 0.05  # Mismo día o día anterior
            if diff <= 7:
                return 0.02  # Misma semana
            return 0.0
        except (ValueError, TypeError):
            return 0.0

    def find_related(self, current_path, tags, category, key_topics,
                     current_date=None):
        """Encuentra notas relacionadas con scoring multi-señal."""
        current = Path(current_path).resolve()
        candidates = []
        weights = self.config.get('weights', {
            'tag_jaccard': 0.40,
            'co_occurrence': 0.30,
            'topic_overlap': 0.20,
            'category_bonus': 0.10,
        })

        for rel, note in self.notes_index.items():
            note_path = note['path'].resolve()
            if note_path == current:
                continue
            if not note_path.exists():
                continue

            tags_a = set(t.lower() for t in tags)
            tags_b = set(t.lower() for t in note['tags'])

            jaccard = self._jaccard(tags_a, tags_b)

            # Si no hay ningún tag en común, skip rápido
            if jaccard == 0 and not (tags_a & tags_b):
                continue

            co_boost = self._co_occurrence_boost(tags, note['tags'])
            topic_score = self._topic_overlap(
                key_topics, note.get('key_topics', [])
            )
            cat_bonus = (
                weights.get('category_bonus', 0.10)
                if category and note.get('category') == category
                else 0.0
            )
            date_bonus = self._date_proximity(
                current_date, note.get('fecha', '')
            )

            combined = (
                weights.get('tag_jaccard', 0.40) * jaccard
                + weights.get('co_occurrence', 0.30) * co_boost
                + weights.get('topic_overlap', 0.20) * topic_score
                + cat_bonus
                + date_bonus
            )

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
        """Construye un wikilink [[nombre]] para Obsidian."""
        name = note_path.stem
        if all_filenames and len(all_filenames.get(name, [])) > 1:
            # Nombre duplicado — usar path relativo
            rel_dir = str(note_path.parent.relative_to(VAULT_ROOT))
            if rel_dir and rel_dir != '.':
                name = f'{rel_dir}/{name}'
        return f'[[{name}]]'

    def build_body_links(self, related):
        """Construye bloque de notas relacionadas como callout de Obsidian.
        
        Usa callout colapsable nativo de Obsidian:
        > [!abstract]- Notas relacionadas
        > [[nota1]] · [[nota2]]
        """
        if not related:
            return ''
        links = []
        all_names = {}
        for r in related:
            n = r['path'].stem
            all_names.setdefault(n, []).append(r['path'])
        for r in related:
            links.append(self.build_wikilink(r['path'], all_names))
        link_text = ' · '.join(links)
        return f'\n\n> [!abstract]- Notas relacionadas\n> {link_text}\n'

    def inject_body_links(self, content, related):
        """Inyecta o actualiza la sección de notas relacionadas.
        
        Usa callout colapsable de Obsidian en vez de markdown crudo.
        Limpia formatos legacy (---/Notas relacionadas) y el nuevo formato.
        """
        if not related:
            return content

        body_links = self.build_body_links(related)
        if not body_links:
            return content

        # 1. Remover formato nuevo (callout)
        content = re.sub(
            r'\n*> \[!abstract\][- ] *Notas relacionadas\n(?:> .*\n?)*',
            '', content
        )

        # 2. Remover formato legacy (---/**Notas relacionadas:**)
        content = re.sub(
            r'\n*---\n+\*\*Notas relacionadas:\*\*[^\n]*\n*',
            '', content
        )

        # 3. Remover --- huérfanos al final
        content = re.sub(r'\n*---\s*$', '', content)

        # 4. Limpiar whitespace al final
        content = content.rstrip('\n')

        # 5. Agregar el nuevo bloque
        return content + body_links
