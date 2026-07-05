#!/usr/bin/env python3
import json
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
            with open(self.registry_path) as f:
                data = json.load(f)
            if data.get('version', '1.0') != '2.0':
                data = self._migrate_v1_to_v2(data)
            return data
        return {'version': '2.0', 'last_updated': '', 'tags': {}, 'categories': {}, 'co_occurrence': {}, 'corrections': [], 'successful_examples': []}

    def _migrate_v1_to_v2(self, old):
        return {'version': '2.0', 'last_updated': old.get('last_updated',''), 'tags': {n: {'count': d.get('count',0), 'successes': d.get('count',1), 'corrections': 0, 'first_seen': d.get('first_seen',''), 'last_seen': d.get('first_seen',''), 'category': d.get('category','uncategorized')} for n,d in old.get('tags',{}).items()}, 'categories': old.get('categories',{}), 'co_occurrence': {}, 'corrections': [], 'successful_examples': []}

    def _save_registry(self):
        self.registry['last_updated'] = datetime.now(timezone.utc).isoformat()
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)

    def _tag_confidence(self, tag):
        d = self.registry['tags'].get(tag, {})
        t = d.get('successes',0) + d.get('corrections',0)
        return d.get('successes',0) / (t + 1) if t else 0.5

    def get_top_tags(self, max_tags=25, min_count=1):
        scored = []
        for n, d in self.registry['tags'].items():
            c = d.get('count',0)
            if c < min_count: continue
            conf = self._tag_confidence(n)
            scored.append((n, c, round(conf, 2), conf * (1 - 1 / (c + 1))))
        scored.sort(key=lambda x: -x[3])
        return scored[:max_tags]

    def get_successful_examples(self, max_examples=3):
        ex = self.registry.get('successful_examples', [])
        ex.sort(key=lambda x: x.get('score', 0), reverse=True)
        return ex[:max_examples]

    def normalize_tag(self, tag):
        return self.aliases.get(tag.lower().strip(), tag.lower().strip())

    def register_classification(self, tags, category=None, user_corrected=False):
        now = datetime.now(timezone.utc).isoformat()
        for tag in tags:
            if tag not in self.registry['tags']:
                self.registry['tags'][tag] = {'count': 0, 'successes': 0, 'corrections': 0, 'first_seen': now, 'last_seen': now, 'category': category or 'uncategorized'}
            d = self.registry['tags'][tag]
            d['count'] = d.get('count', 0) + 1
            d['last_seen'] = now
            if user_corrected: d['corrections'] = d.get('corrections', 0) + 1
            else: d['successes'] = d.get('successes', 0) + 1
            if category: d['category'] = category
        for i, t1 in enumerate(tags):
            for t2 in tags[i+1:]:
                k = f'{tuple(sorted([t1,t2]))[0]}__{tuple(sorted([t1,t2]))[1]}'
                self.registry.setdefault('co_occurrence', {})
                self.registry['co_occurrence'][k] = self.registry['co_occurrence'].get(k, 0) + 1
        self._save_registry()

    def detect_and_register_correction(self, auto_tags, existing_ai_tags, note_path):
        auto_set = set(t.lower() for t in auto_tags)
        existing_set = set(t.lower() for t in existing_ai_tags)
        if not auto_set and not existing_set: return False
        if existing_set and auto_set != existing_set:
            self.register_correction(list(auto_set), list(existing_set), note_path)
            return True
        return False

    def register_correction(self, auto_tags, user_tags, note_path):
        now = datetime.now(timezone.utc).isoformat()
        for t in auto_tags:
            if t in self.registry['tags']:
                self.registry['tags'][t]['corrections'] = self.registry['tags'][t].get('corrections',0) + 1
        for t in user_tags:
            if t not in self.registry['tags']:
                self.registry['tags'][t] = {'count': 1, 'successes': 1, 'corrections': 0, 'first_seen': now, 'last_seen': now, 'category': 'uncategorized'}
            else:
                self.registry['tags'][t]['successes'] = self.registry['tags'][t].get('successes',0) + 1
                self.registry['tags'][t]['last_seen'] = now
        self.registry.setdefault('corrections', [])
        self.registry['corrections'].append({'note': note_path, 'auto': auto_tags, 'user': user_tags, 'timestamp': now})
        self.registry['corrections'] = self.registry['corrections'][-50:]
        self._save_registry()

    def store_example(self, file_path, tags, category, summary, importance, user_verified=False):
        conf_sum = sum(self._tag_confidence(t) for t in tags) / max(len(tags), 1)
        score = (1.5 if user_verified else 1.0) * (0.5 + conf_sum)
        self.registry.setdefault('successful_examples', [])
        self.registry['successful_examples'].append({'file': file_path, 'tags': tags, 'category': category, 'summary': summary, 'importance': importance, 'score': round(score, 3), 'user_verified': user_verified, 'timestamp': datetime.now(timezone.utc).isoformat()})
        self.registry['successful_examples'] = self.registry['successful_examples'][-20:]
        self._save_registry()

    def tag_exists(self, tag):
        return tag in self.registry['tags']
