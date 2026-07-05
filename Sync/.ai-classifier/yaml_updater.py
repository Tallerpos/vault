#!/usr/bin/env python3
"""YAML Updater v3.0 — Preserves field order.

Updates ai_* fields in YAML frontmatter without reordering user fields.
Handles:
- Multiline values (flow and block style)
- Unicode content
- Malformed frontmatter (graceful degradation)
- Preserves exact order of user-defined fields
"""
import re
import yaml


class YAMLUpdater:
    def __init__(self, prefix='ai_', fields=None):
        self.prefix = prefix

    def parse_frontmatter(self, content):
        """Parse YAML frontmatter from content. Returns dict or empty dict."""
        m = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not m:
            return {}
        try:
            result = yaml.safe_load(m.group(1))
            return result if isinstance(result, dict) else {}
        except yaml.YAMLError:
            return {}

    def _format_yaml_value(self, value):
        """Formatea un valor YAML preservando legibilidad para Obsidian."""
        if value is None:
            return ''
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, list):
            if not value:
                return '[]'
            # Listas cortas → flow style [a, b, c]
            # Listas con wikilinks → usar comillas
            items = []
            for v in value:
                v_str = str(v)
                if '[[' in v_str or "'" in v_str or '"' in v_str or ':' in v_str:
                    # Escapar comillas simples duplicándolas
                    escaped = v_str.replace("'", "''")
                    items.append(f"'{escaped}'")
                else:
                    items.append(v_str)
            return '[' + ', '.join(items) + ']'
        # Strings
        s = str(value)
        # Strings que necesitan comillas
        if ('\n' in s or ':' in s or '#' in s or "'" in s or
            s.startswith('{') or s.startswith('[') or s.startswith('*') or
            s.startswith('&') or s.startswith('!') or
            s.strip() != s):
            escaped = s.replace("'", "''")
            return f"'{escaped}'"
        return s

    def update_frontmatter(self, content, ai_fields):
        """Actualiza campos ai_* preservando el orden de los campos del usuario.

        Estrategia:
        1. Parsear el frontmatter original línea por línea
        2. Reemplazar campos ai_* existentes con nuevos valores
        3. Agregar campos ai_* nuevos al final del frontmatter
        4. NUNCA tocar campos del usuario (fecha, tipo, tags, etc.)
        """
        m = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)

        if not m:
            # No hay frontmatter — crear uno nuevo con solo campos AI
            fm_lines = []
            for field, value in ai_fields.items():
                key = f'{self.prefix}{field}'
                fm_lines.append(f'{key}: {self._format_yaml_value(value)}')
            return '---\n' + '\n'.join(fm_lines) + '\n---\n' + content

        original_fm = m.group(1)
        body = content[m.end():]
        lines = original_fm.split('\n')

        new_lines = []
        seen_ai_fields = set()
        skip_continuation = False

        for i, line in enumerate(lines):
            # Detectar si es una clave de nivel superior
            key_match = re.match(r'^(\w[\w_-]*)\s*:', line)

            if key_match:
                key = key_match.group(1)
                skip_continuation = False

                # ¿Es un campo ai_?
                if key.startswith(self.prefix):
                    field = key[len(self.prefix):]
                    if field in ai_fields:
                        # Reemplazar con nuevo valor
                        new_val = self._format_yaml_value(ai_fields[field])
                        new_lines.append(f'{key}: {new_val}')
                        seen_ai_fields.add(field)
                        skip_continuation = True
                        continue
                    else:
                        # Campo ai_ que no estamos actualizando, mantener
                        new_lines.append(line)
                        continue
                else:
                    # Campo del usuario — mantener intacto
                    new_lines.append(line)
                    continue
            else:
                # Línea de continuación (indentada o vacía)
                if skip_continuation:
                    continue  # Saltar continuaciones de campo ai_ reemplazado
                new_lines.append(line)

        # Agregar campos ai_ nuevos que no existían
        for field, value in ai_fields.items():
            if field not in seen_ai_fields:
                key = f'{self.prefix}{field}'
                new_lines.append(f'{key}: {self._format_yaml_value(value)}')

        # Reconstruir
        fm_str = '\n'.join(new_lines)
        return f'---\n{fm_str}\n---\n{body}'
