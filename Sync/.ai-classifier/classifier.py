#!/usr/bin/env python3
import sys, os, json, re, logging
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
from tag_manager import TagManager
from yaml_updater import YAMLUpdater
from api_client import DeepSeekClient

CONFIG_PATH = Path(__file__).parent / 'config.json'
LOG_DIR = Path(__file__).parent / 'logs'
HASH_DIR = Path(__file__).parent / 'cache' / 'hashes'

DEFAULT_SYSTEM_PROMPT = """Eres un clasificador experto de un vault de conocimiento personal.

## CONTEXTO
Tags existentes (PRIORIZA estos):
{existing_tags}

Categorias validas (elige UNA):
{valid_categories}

Ejemplos exitosos previos (sigue este formato):
{few_shot_examples}

## RESPUESTA JSON (solo JSON, sin texto extra)
{{
  "tags": ["tag1", "tag2"],
  "category": "categoria",
  "summary": "Resumen de 1-2 oraciones en espanol.",
  "importance": 3,
  "key_topics": ["tema1", "tema2"]
}}

## REGLAS TAGS
- Espanol, minusculas, guiones, singular. Max {max_tags}
- PRIORIZA tags existentes del vault
- Buenos: "desarrollo-web", "finanzas-personales", "habito-salud"
- Malos: "general", "notas", "apuntes", "importante", "varios"

## CATEGORIAS
{valid_categories}

## IMPORTANCE (1-5)
1=Trivial 2=Baja 3=Media 4=Alta 5=Critica

## SUMMARY: 1-2 oraciones, contexto + accion + proposito. Que se pueda encontrar por busqueda en anos.

## KEY_TOPICS: 2-4 conceptos especificos con guiones. NO repetir tags."""

class NoteClassifier:
    def __init__(self):
        with open(CONFIG_PATH) as f:
            self.config = json.load(f)
        LOG_DIR.mkdir(exist_ok=True)
        HASH_DIR.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=LOG_DIR/'classifier.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.tag_manager = TagManager(self.config['tag_registry']['path'], self.config['tag_registry']['aliases'], self.config.get('learning',{}))
        self.api_client = DeepSeekClient(self.config['api'])
        self.yaml_updater = YAMLUpdater(prefix=self.config['classification']['prefix'])

    def _extract_body(self, content):
        return re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, count=1, flags=re.DOTALL).strip()

    def _content_changed_significantly(self, old, new, thresh=0.5):
        if not old and new: return True
        if old and not new: return True
        if old == new: return False
        ow, nw = set(old.lower().split()), set(new.lower().split())
        if not ow and not nw: return False
        sim = len(ow & nw) / len(ow | nw) if (ow | nw) else 1.0
        return (1 - sim) > thresh

    def _read_body_cache(self, fp):
        cf = HASH_DIR / (fp.name + '.body')
        return cf.read_text(encoding='utf-8') if cf.exists() else ''

    def _write_body_cache(self, fp, body):
        (HASH_DIR / (fp.name + '.body')).write_text(body, encoding='utf-8')

    def _get_existing_ai_tags(self, content):
        return self.yaml_updater.parse_frontmatter(content).get('ai_tags', [])

    def _build_system_prompt(self):
        top = self.tag_manager.get_top_tags(self.config['learning'].get('max_tags_in_prompt',25), 1)
        cats = self.config['classification']['valid_categories']
        mx = self.config['classification']['max_tags']
        ex = self.tag_manager.get_successful_examples(self.config['learning'].get('max_few_shot_examples',3))
        tags_text = '\n'.join(f'  - {n} (usado {c}x, confianza {cf})' for n,c,cf,_ in top) if top else '  (sin tags aun)'
        ex_text = '\n\n'.join(self._format_example(e) for e in ex) if ex else '  (sin ejemplos aun)'
        return DEFAULT_SYSTEM_PROMPT.format(existing_tags=tags_text, valid_categories='\n'.join(f'  - {c}' for c in cats), few_shot_examples=ex_text, max_tags=mx)

    def _format_example(self, ex):
        v = ' (VERIFICADO)' if ex.get('user_verified') else ''
        return f'EJEMPLO{v}:\n  Tags: {json.dumps(ex["tags"], ensure_ascii=False)}\n  Category: {ex.get("category","")}\n  Summary: {ex.get("summary","")}\n  Importance: {ex.get("importance",3)}\n  Key topics: {json.dumps(ex.get("key_topics",[]), ensure_ascii=False)}'

    def _validate_response(self, data):
        cats = self.config['classification']['valid_categories']
        tags = [self.tag_manager.normalize_tag(t) for t in (data.get('tags') or []) if isinstance(t,str) and t.strip()][:self.config['classification']['max_tags']]
        cat = data.get('category','miscelanea') if data.get('category') in cats else 'miscelanea'
        s = (data.get('summary') or '').strip() or 'Sin resumen disponible.'
        imp = max(1, min(5, int(data.get('importance',3)) if isinstance(data.get('importance'),(int,float)) else 3))
        topics = [t.strip() for t in (data.get('key_topics') or []) if isinstance(t,str) and t.strip()][:4]
        return {'tags': tags, 'category': cat, 'summary': s, 'importance': imp, 'key_topics': topics}

    def classify_note(self, file_path):
        try:
            content = file_path.read_text(encoding='utf-8')
            body = self._extract_body(content)
            existing_tags = self._get_existing_ai_tags(content)
            already = bool(existing_tags)
            if already:
                cached = self._read_body_cache(file_path)
                if cached and not self._content_changed_significantly(cached, body, self.config['classification']['reclassify_threshold']):
                    return {'status': 'skipped', 'reason': 'no significant change'}
            classification = self.api_client.classify(self._build_system_prompt(), f'Clasifica esta nota:\n\n{body[:4000]}')
            validated = self._validate_response(classification)
            corrected = False
            if already and existing_tags:
                corrected = self.tag_manager.detect_and_register_correction(validated['tags'], existing_tags, str(file_path))
            fields = {'tags': validated['tags'], 'category': validated['category'], 'summary': validated['summary'], 'importance': validated['importance'], 'key_topics': validated['key_topics'], 'classified_at': datetime.now(timezone.utc).isoformat()}
            file_path.write_text(self.yaml_updater.update_frontmatter(content, fields), encoding='utf-8')
            self._write_body_cache(file_path, body)
            self.tag_manager.register_classification(validated['tags'], validated['category'], user_corrected=corrected)
            self.tag_manager.store_example(str(file_path), validated['tags'], validated['category'], validated['summary'], validated['importance'])
            return {'status': 'success', 'action': 'reclassified' if already else 'classified', 'tags': validated['tags'], 'category': validated['category'], 'summary_length': len(validated['summary']), 'key_topics_count': len(validated['key_topics']), 'user_correction_detected': corrected}
        except Exception as e:
            self.logger.error(f'Classification failed for {file_path}: {e}')
            return {'status': 'error', 'error': str(e)}

def main():
    if len(sys.argv) < 2:
        print('Usage: classifier.py <file_path>'); sys.exit(1)
    fp = Path(sys.argv[1])
    if not fp.exists():
        print(f'{{"status":"error","error":"File not found: {fp}"}}'); sys.exit(1)
    r = NoteClassifier().classify_note(fp)
    print(json.dumps(r, ensure_ascii=False))
    sys.exit(0 if r.get('status') in ('success','skipped') else 1)

if __name__ == '__main__': main()
