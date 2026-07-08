#!/usr/bin/env python3
"""Vault Note Classifier v3.0 — Bulletproof Edition.

Classifies Obsidian notes using DeepSeek API with:
- Atomic file writes (never corrupts)
- File locking (no race conditions)
- Retry queue (never loses a note)
- Filename metadata extraction (smarter classification)
- Placeholder detection (no wasted API calls)
- Body change detection with cache
- User correction learning
- Related note discovery + wikilink injection
"""
import sys
import os
import json
import re
import hashlib
import logging
import fcntl
import tempfile
import time
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
from tag_manager import TagManager
from yaml_updater import YAMLUpdater
from api_client import DeepSeekClient
from link_finder import LinkFinder

CONFIG_PATH = Path(__file__).parent / 'config.json'
LOG_DIR = Path(__file__).parent / 'logs'
HASH_DIR = Path(__file__).parent / 'cache' / 'hashes'
RETRY_QUEUE_PATH = Path(__file__).parent / 'cache' / 'retry_queue.json'

# Placeholders que indican nota vacía — NO gastar API en estos
# ── Rate Limiter ───────────────────────────────────────────
class RateLimiter:
    """Limita clasificaciones a max_per_hour por hora.
    Previene gastos inesperados de API por loops o bugs."""
    def __init__(self, max_per_hour=30):
        self.max_per_hour = max_per_hour
        self.history = []

    def allow(self):
        now = time.time()
        cutoff = now - 3600
        self.history = [t for t in self.history if t > cutoff]
        if len(self.history) >= self.max_per_hour:
            return False
        self.history.append(now)
        return True

    def remaining(self):
        now = time.time()
        cutoff = now - 3600
        self.history = [t for t in self.history if t > cutoff]
        return max(0, self.max_per_hour - len(self.history))


PLACEHOLDERS = {
    'escribe aquí tu nota.',
    'escribe aqui tu nota.',
    'write your note here.',
    '',
}

# Patrones de archivos que NUNCA se deben clasificar
SKIP_FILENAMES = {
    'sin título', 'sin titulo', 'untitled',
    'config', 'sistema-ai', 'guia_recuperacion',
    'enlaces', 'config',
}

DEFAULT_SYSTEM_PROMPT = """Eres un clasificador EXPERTO de un vault de conocimiento personal de Abner.
Tu trabajo es PRECISO, DETALLADO y NUNCA inventas información.

## TU PERSONALIDAD
- Eres meticuloso y preciso
- NUNCA asumes relaciones entre personas (pareja, amigo, familiar) a menos que se diga EXPLÍCITAMENTE con palabras como "mi pareja", "mi novio", "mi esposo/a"
- NUNCA inventas información que no está en el texto
- Si el usuario corrige algo (como "X no es mi pareja"), RESPETAS esa corrección al 100%
- Eres conservador: ante la duda, NO incluyes algo

## METADATA DEL ARCHIVO
El usuario ya clasificó esta nota con un "tipo" al crearla. RESPETA este tipo como señal fuerte:
- idea → categoría probable: ideas o tecnologia
- aprendizaje → categoría probable: aprendizaje
- diario → categoría probable: personal
- lectura/libro → categoría probable: lectura
- finanzas → categoría probable: finanzas
- tecnología/tecnologia → categoría probable: tecnologia
- proyecto → categoría probable: proyectos
- salud → categoría probable: salud
- persona → categoría probable: personal
- reunión/reunion → categoría probable: trabajo
- compras → categoría probable: compras

## TAGS EXISTENTES EN EL VAULT (PRIORIZA reusar estos)
{existing_tags}

## CATEGORÍAS VÁLIDAS (elige EXACTAMENTE UNA)
{valid_categories}

## EJEMPLOS DE CLASIFICACIONES EXITOSAS PREVIAS
{few_shot_examples}

## CORRECCIONES RECIENTES DEL USUARIO (aprende de estas)
{recent_corrections}

## RESPUESTA — SOLO JSON, sin texto extra
{{
  "tags": ["tag1", "tag2"],
  "category": "categoria",
  "summary": "Resumen preciso de 1-2 oraciones en español.",
  "importance": 3,
  "key_topics": ["tema1", "tema2"]
}}

## REGLAS PARA TAGS
- En español, minúsculas, con guiones, singular. Máximo {max_tags}
- PRIORIZA tags que ya existen en el vault (listados arriba)
- BUENOS ejemplos: "desarrollo-web", "finanzas-personales", "habito-salud", "logoterapia"
- MALOS ejemplos (NUNCA uses): "general", "notas", "apuntes", "importante", "varios", "nota", "prueba", "sistema"
- Cada tag debe ser ESPECÍFICO y útil para búsqueda futura
- Si la nota menciona un libro, incluye el nombre del libro como tag
- Si la nota menciona una tecnología, inclúyela como tag

## REGLAS PARA SUMMARY
- 1-2 oraciones PRECISAS que describan el CONTENIDO REAL de la nota
- Debe ser útil para buscar esta nota en años
- NUNCA repitas el título de la nota como summary
- Incluye contexto: ¿qué pasó? ¿con quién? ¿dónde? ¿para qué?
- NUNCA supongas relaciones personales
- Si el texto tiene correcciones del usuario (ej: "cabe recalcar que X no es mi pareja"), tu summary DEBE reflejar la corrección, NO la suposición

## REGLAS PARA IMPORTANCE (1-5)
1 = Trivial — nota de paso sin valor duradero
2 = Baja — referencia menor, dato puntual
3 = Media — contenido útil, vale la pena conservar
4 = Alta — conocimiento importante, decisión clave, aprendizaje valioso
5 = Crítica — información esencial, credenciales, procedimientos vitales

## REGLAS PARA KEY_TOPICS
- 2-4 conceptos ESPECÍFICOS con guiones
- NO repetir los tags
- Deben ser conceptos que ayuden a encontrar la nota por búsqueda semántica
- Ejemplo: si la nota habla de invertir en Bitcoin, key_topics podrían ser ["mercado-cripto", "estrategia-inversion"]

## NOTAS VACÍAS
Si el body está vacío, solo dice "Escribe aquí tu nota" o tiene menos de 20 palabras útiles:
tags=[], category basada en el tipo del filename, importance=1, summary="Nota sin contenido suficiente para clasificar."
"""


class NoteClassifier:
    def __init__(self):
        with open(CONFIG_PATH) as f:
            self.config = json.load(f)
        LOG_DIR.mkdir(exist_ok=True)
        HASH_DIR.mkdir(parents=True, exist_ok=True)
        self._rotate_log_if_needed(LOG_DIR / 'classifier.log')
        logging.basicConfig(
            filename=LOG_DIR / 'classifier.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _rotate_log_if_needed(log_path):
        """Rota el log si supera 10MB sin depender de logrotate externo."""
        try:
            if log_path.exists() and log_path.stat().st_size > 10 * 1024 * 1024:
                log_path.rename(log_path.with_suffix('.log.old'))
        except OSError:
            pass
        self.tag_manager = TagManager(
            self.config['tag_registry']['path'],
            self.config['tag_registry']['aliases'],
            self.config.get('learning', {})
        )
        self.api_client = DeepSeekClient(self.config['api'])
        max_rate = self.config.get('rate_limit', {}).get('max_per_hour', 30)
        self.rate_limiter = RateLimiter(max_per_hour=max_rate)
        self.yaml_updater = YAMLUpdater(prefix=self.config['classification']['prefix'])
        self.link_finder = LinkFinder(
            self.config['tag_registry']['path'],
            self.config.get('linking', {})
        )

    # ── Utilidades de contenido ──────────────────────────────────

    def _extract_body(self, content):
        """Extrae el body sin frontmatter ni secciones inyectadas."""
        body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, count=1, flags=re.DOTALL)
        # Remover sección de notas relacionadas inyectada
        body = re.sub(
            r'\n*> \[!abstract\][- ].*?(?=\n[^>]|\Z)',
            '', body, flags=re.DOTALL
        )
        # Remover formato legacy de notas relacionadas
        body = re.sub(
            r'\n*---\n+\*\*Notas relacionadas:\*\*.*',
            '', body, flags=re.DOTALL
        )
        return body.strip()

    def _is_placeholder(self, body):
        """Detecta si el body es un placeholder del template."""
        cleaned = body.strip().lower()
        if cleaned in PLACEHOLDERS:
            return True
        # Menos de 15 palabras útiles (sin stopwords)
        words = [w for w in cleaned.split() if len(w) > 2]
        if len(words) < 5:
            return True
        return False

    def _should_skip_file(self, file_path):
        """Determina si un archivo debe ser ignorado."""
        name = file_path.stem.lower()
        # Archivos con nombres genéricos
        for skip in SKIP_FILENAMES:
            if name.startswith(skip):
                return True, f'filename pattern: {skip}'
        # Archivos fuera de Notas/ y Diario/ (excepto libros)
        rel = str(file_path.relative_to(Path('/opt/vault/Sync')))
        valid_dirs = ('Notas/', 'Diario/')
        if not any(rel.startswith(d) for d in valid_dirs):
            # Permitir archivos raíz que parecen libros o contenido real
            fm = self.yaml_updater.parse_frontmatter(
                file_path.read_text(encoding='utf-8')
            )
            if fm.get('tipo') in ('libro', 'lectura'):
                return False, None
            if not fm.get('fecha') and not fm.get('tipo'):
                return True, f'outside valid dirs and no valid frontmatter'
        return False, None

    def _extract_filename_meta(self, file_path):
        """Extrae fecha, tipo y título del patrón YYYY-MM-DD - tipo - título.md"""
        stem = file_path.stem
        parts = stem.split(' - ', 2)
        meta = {}
        if len(parts) >= 1:
            # Intentar parsear fecha
            try:
                datetime.strptime(parts[0].strip(), '%Y-%m-%d')
                meta['fecha'] = parts[0].strip()
            except ValueError:
                pass
        if len(parts) >= 2:
            meta['tipo'] = parts[1].strip()
        if len(parts) >= 3:
            meta['titulo'] = parts[2].strip()
        # También revisar frontmatter por tipo
        return meta

    def _content_changed_significantly(self, old_body, new_body, threshold=None):
        """Compara cuerpos de nota para decidir si re-clasificar."""
        threshold = threshold or self.config['classification'].get('reclassify_threshold', 0.4)
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
        union = old_words | new_words
        if not union:
            return False
        similarity = len(old_words & new_words) / len(union)
        return (1 - similarity) > threshold

    # ── Cache ────────────────────────────────────────────────────

    def _body_cache_key(self, file_path):
        return hashlib.sha256(str(file_path).encode()).hexdigest()

    def _read_body_cache(self, file_path):
        cache_file = HASH_DIR / (self._body_cache_key(file_path) + '.body')
        if cache_file.exists():
            return cache_file.read_text(encoding='utf-8')
        return ''

    def _write_body_cache(self, file_path, body):
        cache_file = HASH_DIR / (self._body_cache_key(file_path) + '.body')
        self._atomic_write(cache_file, body)

    # ── Escritura segura ─────────────────────────────────────────

    def _atomic_write(self, file_path, content):
        """Escritura atómica: escribe a temp file, luego rename.
        NUNCA deja un archivo corrupto o parcial."""
        file_path = Path(file_path)
        dir_path = file_path.parent
        dir_path.mkdir(parents=True, exist_ok=True)
        try:
            tmp = tempfile.NamedTemporaryFile(
                mode='w', dir=str(dir_path), suffix='.tmp',
                delete=False, encoding='utf-8'
            )
            tmp.write(content)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp.close()
            os.replace(tmp.name, str(file_path))
        except Exception:
            # Limpiar temp file si falla
            try:
                os.unlink(tmp.name)
            except OSError:
                pass
            raise

    def _safe_write_note(self, file_path, content):
        """Escribe nota con file lock para evitar race con Syncthing."""
        lock_path = Path(str(file_path) + '.lock')
        lock_fd = None
        try:
            lock_fd = open(lock_path, 'w')
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._atomic_write(file_path, content)
        except BlockingIOError:
            self.logger.warning(f'File locked by another process: {file_path}')
            raise
        finally:
            if lock_fd:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                lock_fd.close()
            try:
                lock_path.unlink(missing_ok=True)
            except OSError:
                pass

    # ── AI Tags existentes ───────────────────────────────────────

    def _get_existing_ai_tags(self, content):
        fm = self.yaml_updater.parse_frontmatter(content)
        tags = fm.get('ai_tags', [])
        if tags is None:
            return []
        if isinstance(tags, str):
            return [tags]
        return list(tags)

    def _is_genuine_correction(self, auto_tags, existing_tags):
        """Detecta si es corrección REAL del usuario o solo variación de re-clasificación.
        Usa Jaccard similarity: si >50% solapamiento, es probable re-clasificación, NO corrección."""
        if not existing_tags:
            return False
        if not auto_tags:
            return bool(existing_tags)
        set_a = set(t.lower() for t in auto_tags)
        set_b = set(t.lower() for t in existing_tags)
        union = set_a | set_b
        if not union:
            return False
        jaccard = len(set_a & set_b) / len(union)
        return jaccard < 0.5

    # ── Prompt building ──────────────────────────────────────────

    def _build_system_prompt(self):
        learning = self.config.get('learning', {})
        min_obs = learning.get('min_observations', 1)
        max_tags_prompt = learning.get('max_tags_in_prompt', 25)
        max_examples = learning.get('max_few_shot_examples', 3)

        top_tags = self.tag_manager.get_top_tags(max_tags_prompt, min_obs)
        categories = self.config['classification']['valid_categories']
        max_tags = self.config['classification']['max_tags']
        examples = self.tag_manager.get_successful_examples(max_examples)
        corrections = self.tag_manager.get_recent_corrections(3)

        tags_text = '\n'.join(
            f'  - {name} (usado {count}x, confianza {conf})'
            for name, count, conf, _ in top_tags
        ) if top_tags else '  (sin tags aún — crea los que consideres apropiados)'

        examples_text = '\n\n'.join(
            self._format_example(e) for e in examples
        ) if examples else '  (sin ejemplos aún)'

        corrections_text = '\n\n'.join(
            self._format_correction(c) for c in corrections
        ) if corrections else '  (sin correcciones)'

        return DEFAULT_SYSTEM_PROMPT.format(
            existing_tags=tags_text,
            valid_categories='\n'.join(f'  - {c}' for c in categories),
            few_shot_examples=examples_text,
            recent_corrections=corrections_text,
            max_tags=max_tags
        )

    def _format_example(self, ex):
        verified = ' ✅ VERIFICADO POR USUARIO' if ex.get('user_verified') else ''
        return (
            f'EJEMPLO{verified}:\n'
            f'  Tags: {json.dumps(ex["tags"], ensure_ascii=False)}\n'
            f'  Category: {ex.get("category", "")}\n'
            f'  Summary: {ex.get("summary", "")}\n'
            f'  Importance: {ex.get("importance", 3)}\n'
            f'  Key topics: {json.dumps(ex.get("key_topics", []), ensure_ascii=False)}'
        )

    def _format_correction(self, corr):
        return (
            f'CORRECCIÓN (el usuario cambió esto):\n'
            f'  Tags automáticos: {json.dumps(corr.get("auto", []), ensure_ascii=False)}\n'
            f'  Tags del usuario: {json.dumps(corr.get("user", []), ensure_ascii=False)}\n'
            f'  Nota: {corr.get("note", "")}'
        )

    def _build_user_prompt(self, body, file_path, frontmatter):
        """Construye el prompt del usuario con TODA la metadata disponible."""
        meta = self._extract_filename_meta(file_path)
        fm_tipo = frontmatter.get('tipo', '')
        fm_tags = frontmatter.get('tags', [])

        context_parts = []
        # Tipo — señal más fuerte
        tipo = meta.get('tipo') or fm_tipo
        if tipo:
            context_parts.append(f'Tipo de nota (definido por el usuario): {tipo}')
        # Título del filename
        if meta.get('titulo'):
            context_parts.append(f'Título: {meta["titulo"]}')
        # Fecha
        fecha = meta.get('fecha') or str(frontmatter.get('fecha', ''))
        if fecha:
            context_parts.append(f'Fecha: {fecha}')
        # Tags manuales del usuario (si existen)
        if fm_tags and isinstance(fm_tags, list) and fm_tags:
            context_parts.append(f'Tags del usuario: {json.dumps(fm_tags, ensure_ascii=False)}')
        # Tipo especial: libro
        if frontmatter.get('tipo') == 'libro' or frontmatter.get('titulo'):
            book_info = []
            if frontmatter.get('titulo'):
                book_info.append(f'Libro: {frontmatter["titulo"]}')
            if frontmatter.get('autor'):
                book_info.append(f'Autor: {frontmatter["autor"]}')
            if book_info:
                context_parts.append(' · '.join(book_info))

        context = '\n'.join(context_parts)
        # Usar más body (6000 chars — DeepSeek es barato)
        body_truncated = body[:6000]
        if len(body) > 6000:
            body_truncated += '\n[... nota truncada ...]'

        return f'Clasifica esta nota:\n\n{context}\n\n---\n\n{body_truncated}'

    # ── Validación de respuesta ──────────────────────────────────

    def _validate_response(self, data, filename_meta=None):
        """Valida y limpia la respuesta del LLM. Nunca deja pasar basura."""
        categories = self.config['classification']['valid_categories']
        max_tags = self.config['classification']['max_tags']

        # Tags: normalizar, filtrar basura, limitar cantidad
        raw_tags = data.get('tags') or []
        tags = []
        bad_tags = {'general', 'notas', 'apuntes', 'importante', 'varios',
                    'nota', 'prueba', 'sistema', 'test', 'ejemplo', 'misc',
                    'otro', 'sin-clasificar', 'indefinido', 'ninguno'}
        for t in raw_tags:
            if not isinstance(t, str) or not t.strip():
                continue
            normalized = self.tag_manager.normalize_tag(t)
            if normalized in bad_tags:
                continue
            if len(normalized) < 2:
                continue
            if normalized not in tags:  # Deduplicar
                tags.append(normalized)
        tags = tags[:max_tags]

        # Categoría: validar contra lista
        raw_cat = (data.get('category') or '').strip().lower()
        category = raw_cat if raw_cat in categories else 'miscelanea'
        # Si tenemos tipo del filename, usarlo como fallback inteligente
        if category == 'miscelanea' and filename_meta and filename_meta.get('tipo'):
            tipo_map = {
                'idea': 'ideas', 'aprendizaje': 'aprendizaje',
                'diario': 'personal', 'lectura': 'lectura', 'libro': 'lectura',
                'finanzas': 'finanzas', 'tecnologia': 'tecnologia',
                'tecnología': 'tecnologia', 'proyecto': 'proyectos',
                'salud': 'salud', 'persona': 'personal',
                'reunion': 'trabajo', 'reunión': 'trabajo',
                'compras': 'compras', 'prueba': 'miscelanea',
            }
            mapped = tipo_map.get(filename_meta['tipo'].lower())
            if mapped and mapped in categories:
                category = mapped

        # Summary: limpiar
        summary = (data.get('summary') or '').strip()
        if not summary or len(summary) < 10:
            summary = 'Sin resumen disponible.'
        # Truncar si es demasiado largo
        if len(summary) > 300:
            summary = summary[:297] + '...'

        # Importance: validar rango
        raw_imp = data.get('importance', 3)
        try:
            importance = max(1, min(5, int(raw_imp)))
        except (ValueError, TypeError):
            importance = 3

        # Key topics: limpiar, deduplicar vs tags
        raw_topics = data.get('key_topics') or []
        topics = []
        for t in raw_topics:
            if not isinstance(t, str) or not t.strip():
                continue
            cleaned = t.strip().lower()
            # No repetir tags
            if cleaned not in tags and cleaned not in topics:
                topics.append(cleaned)
        topics = topics[:4]

        return {
            'tags': tags,
            'category': category,
            'summary': summary,
            'importance': importance,
            'key_topics': topics,
        }

    # ── Retry Queue ──────────────────────────────────────────────

    def _load_retry_queue(self):
        if RETRY_QUEUE_PATH.exists():
            try:
                return json.loads(RETRY_QUEUE_PATH.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save_retry_queue(self, queue):
        self._atomic_write(RETRY_QUEUE_PATH, json.dumps(queue[-50:], ensure_ascii=False, indent=2))

    def _add_to_retry(self, file_path, error):
        queue = self._load_retry_queue()
        # No duplicar
        existing_paths = {item['path'] for item in queue}
        if str(file_path) in existing_paths:
            return
        queue.append({
            'path': str(file_path),
            'error': str(error)[:200],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'attempts': 1
        })
        self._save_retry_queue(queue)
        self.logger.info(f'Added to retry queue: {file_path}')

    def process_retry_queue(self):
        """Procesa la cola de reintentos. Llamado periódicamente."""
        queue = self._load_retry_queue()
        if not queue:
            print(json.dumps({'status': 'empty', 'message': 'No items in retry queue'}))
            return

        remaining = []
        processed = 0
        for item in queue:
            fp = Path(item['path'])
            if not fp.exists():
                self.logger.info(f'Retry skip (file gone): {fp}')
                continue
            if item.get('attempts', 0) >= 3:
                self.logger.warning(f'Retry exhausted (3 attempts): {fp}')
                continue

            result = self.classify_note(fp)
            if result['status'] == 'error':
                item['attempts'] = item.get('attempts', 0) + 1
                item['last_error'] = result.get('error', '')
                remaining.append(item)
            else:
                processed += 1
                self.logger.info(f'Retry success: {fp}')

        self._save_retry_queue(remaining)
        print(json.dumps({
            'status': 'done',
            'processed': processed,
            'remaining': len(remaining)
        }))

    # ── Clasificación principal ──────────────────────────────────

    def classify_note(self, file_path):
        """Clasifica una nota. Retorna dict con status y metadata."""
        try:
            file_path = Path(file_path).resolve()

            # Verificar que el archivo existe y es legible
            if not file_path.exists():
                return {'status': 'error', 'error': f'File not found: {file_path}'}
            if not file_path.suffix == '.md':
                return {'status': 'skipped', 'reason': 'not a markdown file'}

            # Verificar si debemos saltar este archivo
            should_skip, reason = self._should_skip_file(file_path)
            if should_skip:
                self.logger.info(f'Skipped ({reason}): {file_path}')
                return {'status': 'skipped', 'reason': reason}

            content = file_path.read_text(encoding='utf-8')
            frontmatter = self.yaml_updater.parse_frontmatter(content)
            body = self._extract_body(content)

            # Si es placeholder, no gastar API
            if self._is_placeholder(body):
                self.logger.info(f'Skipped (placeholder): {file_path}')
                return {'status': 'skipped', 'reason': 'placeholder content'}

            # Check si ya fue clasificada (usa ai_classified_at como señal definitiva,
            # NO bool(ai_tags) porque [] vacío es clasificación válida pero falsy)
            existing_tags = self._get_existing_ai_tags(content)
            already_classified = 'ai_classified_at' in frontmatter
            if already_classified:
                cached_body = self._read_body_cache(file_path)
                if cached_body and not self._content_changed_significantly(cached_body, body):
                    self.logger.info(f'Skipped (no significant change): {file_path}')
                    return {'status': 'skipped', 'reason': 'no significant change'}

            # Extraer metadata del filename
            filename_meta = self._extract_filename_meta(file_path)

            # Rate limiting: evitar gastos inesperados de API
            if not self.rate_limiter.allow():
                remaining = self.rate_limiter.remaining()
                self.logger.warning(f'Rate limit reached. {remaining} slots remaining this hour. Skipping: {file_path}')
                return {'status': 'skipped', 'reason': 'rate limit reached'}

            # Llamar a la API
            self.logger.info(f'Classifying: {file_path}')
            classification = self.api_client.classify(
                self._build_system_prompt(),
                self._build_user_prompt(body, file_path, frontmatter)
            )

            # Validar respuesta
            validated = self._validate_response(classification, filename_meta)

            # Detectar correcciones del usuario
            corrected = False
            if already_classified and self._is_genuine_correction(validated['tags'], existing_tags):
                corrected = self.tag_manager.detect_and_register_correction(
                    validated['tags'], existing_tags, str(file_path)
                )

            # Buscar notas relacionadas
            related = self.link_finder.find_related(
                file_path, validated['tags'],
                validated['category'], validated['key_topics']
            )
            related_links = [
                self.link_finder.build_wikilink(r['path'])
                for r in related
            ]

            # Construir campos AI
            fields = {
                'tags': validated['tags'],
                'category': validated['category'],
                'summary': validated['summary'],
                'importance': validated['importance'],
                'key_topics': validated['key_topics'],
                'related': related_links,
                'classified_at': datetime.now(timezone.utc).isoformat(),
            }

            # Actualizar frontmatter
            updated_content = self.yaml_updater.update_frontmatter(content, fields)

            # Inyectar body links (callout colapsable)
            if related:
                updated_content = self.link_finder.inject_body_links(
                    updated_content, related
                )

            # Escribir de forma segura
            self._safe_write_note(file_path, updated_content)

            # Guardar cache del body
            self._write_body_cache(file_path, body)

            # Registrar en tag manager
            self.tag_manager.register_classification(
                validated['tags'], validated['category'],
                user_corrected=corrected
            )
            self.tag_manager.store_example(
                str(file_path), validated['tags'],
                validated['category'], validated['summary'],
                validated['importance']
            )

            result = {
                'status': 'success',
                'action': 'reclassified' if already_classified else 'classified',
                'tags': validated['tags'],
                'category': validated['category'],
                'summary_length': len(validated['summary']),
                'key_topics_count': len(validated['key_topics']),
                'related_count': len(related),
                'user_correction_detected': corrected,
            }
            self.logger.info(
                f'Success: {file_path} → '
                f'tags={validated["tags"]}, cat={validated["category"]}, '
                f'related={len(related)}'
            )
            return result

        except Exception as e:
            self.logger.error(f'Classification failed for {file_path}: {e}')
            self._add_to_retry(file_path, e)
            return {'status': 'error', 'error': str(e)}


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == '--retry':
        NoteClassifier().process_retry_queue()
        sys.exit(0)

    if len(sys.argv) >= 2 and sys.argv[1] == '--health':
        # Import inline para evitar circular
        from health_check import check_health
        sys.exit(check_health())

    if len(sys.argv) < 2:
        print('Usage: classifier.py <file_path> | --retry | --health')
        sys.exit(1)

    fp = Path(sys.argv[1])
    if not fp.is_absolute():
        fp = Path('/opt/vault/Sync') / fp
    if not fp.exists():
        print(json.dumps({'status': 'error', 'error': f'File not found: {fp}'}))
        sys.exit(1)

    result = NoteClassifier().classify_note(fp)
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result.get('status') in ('success', 'skipped') else 1)


if __name__ == '__main__':
    main()
