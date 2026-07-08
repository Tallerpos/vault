#!/usr/bin/env python3
"""Tag Manager v3.0 — Atomic writes, better learning.

Manages:
- Tag registry with usage stats and confidence scores
- Tag normalization via aliases
- Co-occurrence tracking
- User correction learning
- Successful example storage for few-shot learning
"""
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone


class TagManager:
    def __init__(self, registry_path, aliases, learning_config=None):
        self.registry_path = Path(registry_path)
        self.aliases = aliases
        self.learning_config = learning_config or {}
        self.registry = self._load_registry()

    def _load_registry(self):
        if self.registry_path.exists():
            try:
                with open(self.registry_path) as f:
                    data = json.load(f)
                if data.get('version', '1.0') != '2.0':
                    data = self._migrate_v1_to_v2(data)
                return data
            except (json.JSONDecodeError, OSError):
                # Registry corrupto — empezar de cero
                return self._empty_registry()
        return self._empty_registry()

    def _empty_registry(self):
        return {
            'version': '2.0',
            'last_updated': '',
            'tags': {},
            'categories': {},
            'co_occurrence': {},
            'corrections': [],
            'successful_examples': [],
        }

    def _migrate_v1_to_v2(self, old):
        return {
            'version': '2.0',
            'last_updated': old.get('last_updated', ''),
            'tags': {
                name: {
                    'count': d.get('count', 0),
                    'successes': d.get('count', 1),
                    'corrections': 0,
                    'first_seen': d.get('first_seen', ''),
                    'last_seen': d.get('first_seen', ''),
                    'category': d.get('category', 'uncategorized'),
                }
                for name, d in old.get('tags', {}).items()
            },
            'categories': old.get('categories', {}),
            'co_occurrence': {},
            'corrections': [],
            'successful_examples': [],
        }

    def _save_registry(self):
        """Escritura atómica del registry — NUNCA corrompe el archivo."""
        self.registry['last_updated'] = datetime.now(timezone.utc).isoformat()
        try:
            tmp = tempfile.NamedTemporaryFile(
                mode='w', dir=str(self.registry_path.parent),
                suffix='.tmp', delete=False, encoding='utf-8'
            )
            json.dump(self.registry, tmp, indent=2, ensure_ascii=False)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp.close()
            os.replace(tmp.name, str(self.registry_path))
        except Exception:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass
            raise

    def _tag_confidence(self, tag):
        """Calcula confianza de un tag basado en éxitos vs correcciones."""
        d = self.registry['tags'].get(tag, {})
        successes = d.get('successes', 0)
        corrections = d.get('corrections', 0)
        total = successes + corrections
        if total == 0:
            return 0.5  # Sin datos, confianza neutral
        return successes / (total + 1)

    def get_top_tags(self, max_tags=25, min_count=1):
        """Retorna los tags más relevantes ordenados por score."""
        scored = []
        for name, d in self.registry['tags'].items():
            count = d.get('count', 0)
            if count < min_count:
                continue
            conf = self._tag_confidence(name)
            # Score: confianza ponderada por frecuencia
            score = conf * (1 - 1 / (count + 1))
            scored.append((name, count, round(conf, 2), score))
        scored.sort(key=lambda x: -x[3])
        return scored[:max_tags]

    def get_successful_examples(self, max_examples=3):
        """Retorna los mejores ejemplos para few-shot learning."""
        examples = self.registry.get('successful_examples', [])
        examples.sort(key=lambda x: x.get('score', 0), reverse=True)
        return examples[:max_examples]

    def get_recent_corrections(self, max_corrections=3):
        """Retorna las correcciones más recientes para que el LLM aprenda."""
        corrections = self.registry.get('corrections', [])
        return corrections[-max_corrections:]

    def normalize_tag(self, tag):
        """Normaliza un tag usando aliases configurados."""
        normalized = tag.lower().strip()
        return self.aliases.get(normalized, normalized)

    def register_classification(self, tags, category=None, user_corrected=False):
        """Registra una clasificación exitosa."""
        now = datetime.now(timezone.utc).isoformat()
        for tag in tags:
            if tag not in self.registry['tags']:
                self.registry['tags'][tag] = {
                    'count': 0,
                    'successes': 0,
                    'corrections': 0,
                    'first_seen': now,
                    'last_seen': now,
                    'category': category or 'uncategorized',
                }
            d = self.registry['tags'][tag]
            d['count'] = d.get('count', 0) + 1
            d['last_seen'] = now
            if user_corrected:
                d['corrections'] = d.get('corrections', 0) + 1
            else:
                d['successes'] = d.get('successes', 0) + 1
            if category:
                d['category'] = category

        # Registrar co-occurrence entre pares de tags
        self._update_co_occurrence(tags)
        self._save_registry()

    def _update_co_occurrence(self, tags):
        """Actualiza la matriz de co-occurrence."""
        co = self.registry.setdefault('co_occurrence', {})
        for i, t1 in enumerate(tags):
            for t2 in tags[i + 1:]:
                key = '__'.join(sorted([t1, t2]))
                co[key] = co.get(key, 0) + 1

    def detect_and_register_correction(self, auto_tags, existing_ai_tags, note_path):
        """Detecta si el usuario corrigió los tags y registra la corrección."""
        auto_set = set(t.lower() for t in auto_tags)
        existing_set = set(t.lower() for t in existing_ai_tags)
        if not auto_set and not existing_set:
            return False
        if existing_set and auto_set != existing_set:
            self.register_correction(list(auto_set), list(existing_set), note_path)
            return True
        return False

    def register_correction(self, auto_tags, user_tags, note_path):
        """Registra una corrección del usuario para aprendizaje."""
        now = datetime.now(timezone.utc).isoformat()
        # Penalizar tags que el usuario eliminó
        for t in auto_tags:
            if t in self.registry['tags']:
                self.registry['tags'][t]['corrections'] = (
                    self.registry['tags'][t].get('corrections', 0) + 1
                )
        # Premiar tags que el usuario agregó
        for t in user_tags:
            if t not in self.registry['tags']:
                self.registry['tags'][t] = {
                    'count': 1, 'successes': 1, 'corrections': 0,
                    'first_seen': now, 'last_seen': now,
                    'category': 'uncategorized',
                }
            else:
                self.registry['tags'][t]['successes'] = (
                    self.registry['tags'][t].get('successes', 0) + 1
                )
                self.registry['tags'][t]['last_seen'] = now

        # Guardar la corrección para few-shot
        self.registry.setdefault('corrections', [])
        self.registry['corrections'].append({
            'note': note_path,
            'auto': auto_tags,
            'user': user_tags,
            'timestamp': now,
        })
        # Mantener solo las últimas 50
        self.registry['corrections'] = self.registry['corrections'][-50:]
        self._save_registry()

    def store_example(self, file_path, tags, category, summary, importance,
                      user_verified=False):
        """Almacena un ejemplo exitoso para few-shot learning."""
        conf_sum = sum(self._tag_confidence(t) for t in tags) / max(len(tags), 1)
        score = (1.5 if user_verified else 1.0) * (0.5 + conf_sum)

        self.registry.setdefault('successful_examples', [])
        self.registry['successful_examples'].append({
            'file': file_path,
            'tags': tags,
            'category': category,
            'summary': summary,
            'importance': importance,
            'score': round(score, 3),
            'user_verified': user_verified,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })
        # Mantener solo los últimos 20
        self.registry['successful_examples'] = (
            self.registry['successful_examples'][-20:]
        )
        self._save_registry()

    def tag_exists(self, tag):
        return tag in self.registry['tags']

    def get_co_occurrence(self, tag1, tag2):
        """Retorna la cuenta de co-occurrence entre dos tags."""
        key = '__'.join(sorted([tag1, tag2]))
        return self.registry.get('co_occurrence', {}).get(key, 0)
