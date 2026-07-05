# Sistema de Clasificación AI - Second Brain

## Arquitectura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Obsidian   │────▶│  Syncthing   │────▶│   VPS (torrepaginox) │
│  (móvil/PC)  │◀────│  (Sync)      │◀────│   /opt/vault/Sync    │
└─────────────┘     └──────────────┘     └─────────────────┘
                                                  │
                                         ┌────────┴────────┐
                                         │                  │
                                    ┌────▼────┐      ┌─────▼──────┐
                                    │ai-watcher│      │vault-watcher│
                                    │(classify)│      │(git backup) │
                                    └────┬────┘      └─────┬──────┘
                                         │                  │
                                    ┌────▼────┐      ┌─────▼──────┐
                                    │DeepSeek │      │  GitHub    │
                                    │  API    │      │  (backup)  │
                                    └─────────┘      └────────────┘
```

## Flujo de datos

### Clasificación automática
1. Creas nota en Obsidian (móvil/PC) con Templater
2. Syncthing sincroniza a VPS (`/opt/vault/Sync/`)
3. `ai-watcher` detecta cambio via inotifywait
4. Espera 60s (debounce) para consolidar cambios
5. `classifier.py` ejecuta:
   - Extrae contenido de la nota
   - Compara con body cache (¿ya fue clasificada?)
   - Si cambió significativamente (>40% diferente) → re-clasifica
   - Envía a DeepSeek API para clasificación
   - Valida respuesta (tags, categoría, resumen, importancia)
   - **Busca notas relacionadas** (tag overlap + co-occurrence)
   - Actualiza YAML con campos `ai_*`
   - Inyecta `ai_related` con wikilinks `[[...]]`
   - Agrega links al final del body de la nota
   - Actualiza tag registry con nuevos tags y co-occurrence
6. `vault-watcher` detecta cambio → git add/commit/push a GitHub

### Enlazador de notas
- Usa **tag overlap** (Jaccard similarity) como señal principal
- Boost por **co-occurrence** (si tags A y B aparecen juntos seguido)
- Score por **key_topics** compartidos
- Bonus por **misma categoría**
- Umbral mínimo: 0.35 (configurable)
- Máximo 5 enlaces por nota
- Nunca fabrica nombres de archivo — solo usa paths reales del vault

## Componentes

### Archivos principales

| Archivo | Función |
|---------|---------|
| `ai-watcher.sh` (v4.0) | Daemon que detecta cambios y ejecuta classifier |
| `.ai-classifier/classifier.py` | Motor principal de clasificación |
| `.ai-classifier/api_client.py` | Cliente para DeepSeek API |
| `.ai-classifier/tag_manager.py` | Gestión de tags, aliases, co-occurrence |
| `.ai-classifier/link_finder.py` | Buscador de notas relacionadas |
| `.ai-classifier/yaml_updater.py` | Actualizador de frontmatter YAML |
| `.ai-classifier/config.json` | Configuración del sistema |
| `.tag-registry.json` | Registro de tags con métricas |
| `Templates/Nota Minimalista.md` | Plantilla Templater |

### Servicios systemd

| Servicio | Función |
|----------|---------|
| `ai-watcher.service` | Clasificación automática (user: abner) |
| `vault-watcher.service` | Backup a GitHub (user: abner) |

### Archivos de configuración

| Archivo | Descripción |
|---------|-------------|
| `/etc/ai-classifier.env` | API key de DeepSeek (chmod 600) |
| `/etc/vault-watcher.env` | PAT de GitHub (chmod 600) |

## Configuración

### Categories válidas
`personal`, `trabajo`, `finanzas`, `tecnologia`, `aprendizaje`, `ideas`, `salud`, `ocio`, `familia`, `proyectos`, `compras`, `viajes`, `lectura`, `desarrollo`, `miscelanea`

### Tag Aliases (deduplicación)
- `finanza/finanzas/economía/finance` → `economia`
- `programación/programming/coding/dev` → `programacion`
- `ia/ai/machine-learning/ml` → `inteligencia-artificial`
- `automatización` → `automatizacion`
- `clasificación` → `clasificacion`
- `inversión` → `inversion`

### Importancia (1-5)
1. Trivial — nota快速 de paso
2. Baja — referencia menor
3. Media — contenido útil
4. Alta — conocimiento importante
5. Crítica — información esencial

## Comandos útiles

```bash
# Reiniciar watchers
sudo systemctl restart ai-watcher
sudo systemctl restart vault-watcher

# Ver logs en tiempo real
tail -f /opt/vault/Sync/.ai-classifier/logs/watcher.log
tail -f /opt/vault/Sync/.ai-classifier/logs/classifier.log

# Clasificar una nota manualmente
export DEEPSEEK_API_KEY=$(grep DEEPSEEK_API_KEY /etc/ai-classifier.env | cut -d= -f2)
cd /opt/vault/Sync
python3 .ai-classifier/classifier.py "Notas/nota-ejemplo.md"

# Verificar estado de servicios
sudo systemctl status ai-watcher vault-watcher

# Limpiar cache de hashes
rm -f /opt/vault/Sync/.ai-classifier/cache/hashes/*

# Corregir permisos
sudo chown -R abner:abner /opt/vault/

# Ver tag registry
cat /opt/vault/Sync/.tag-registry.json | python3 -m json.tool

# Buscar notas con un tag específico
grep -rl "ai_tags:.*inteligencia-artificial" /opt/vault/Sync/Notas/
```

## Solución de problemas

### Permission denied
```bash
sudo chown -R abner:abner /opt/vault/
```

### No clasifica (no aparecen ai_ fields)
1. Verificar servicio: `sudo systemctl status ai-watcher`
2. Verificar API key: `cat /etc/ai-classifier.env`
3. Verificar logs: `tail -20 .ai-classifier/logs/watcher.log`
4. Probar manual: `python3 .ai-classifier/classifier.py "ruta/nota.md"`

### Tags duplicadas
Verificar aliases en `.ai-classifier/config.json` → `tag_registry.aliases`

### Vault-watcher no sube a GitHub
1. Verificar servicio: `sudo systemctl status vault-watcher`
2. Verificar PAT: `cat /etc/vault-watcher.env`
3. Verificar git: `cd /opt/vault && git status`

### Notas no se enlazan
- Verificar que las notas tienen `ai_tags` en YAML
- El enlazador necesita al menos 2 tags compartidos o co-occurrence
- Umbral mínimo: score 0.35
- Verificar en logs: `grep "related=" .ai-classifier/logs/watcher.log`

## Estructura del vault

```
/opt/vault/Sync/
├── CONFIG.md                    # Config SilverBullet
├── ENLACES.md                   # Enlaces guardados
├── El hombre en busca de sentido.md
├── Guia_Recuperacion.md
├── Diario/
│   └── YYYY-MM-DD.md           # Notas diarias
├── Notas/
│   └── YYYY-MM-DD - tipo - título.md
├── Adjuntos/                    # Archivos adjuntos
├── Templates/
│   └── Nota Minimalista.md     # Plantilla Templater
├── .ai-classifier/
│   ├── classifier.py           # Motor de clasificación
│   ├── api_client.py           # Cliente DeepSeek
│   ├── tag_manager.py          # Gestión de tags
│   ├── link_finder.py          # Buscador de relaciones
│   ├── yaml_updater.py         # Actualizador YAML
│   ├── config.json             # Configuración
│   ├── cache/hashes/           # Cache de cambios
│   └── logs/                   # Logs
└── .tag-registry.json          # Registro de tags
```

## YAML Frontmatter (campos AI)

```yaml
---
fecha: 2026-07-04
tipo: idea
tags: []
relacionado: []
ai_tags: [inteligencia-artificial, automatizacion]
ai_category: tecnologia
ai_summary: Nota sobre el uso de IA para clasificar notas.
ai_importance: 3
ai_key_topics: [obsidian, clasificacion-automatica]
ai_related: ["[[Otra-nota-relacionada]]"]
ai_classified_at: '2026-07-05T00:44:49.194496+00:00'
---
```

## Costo estimado

- DeepSeek Chat API: ~$0.30/mes (clasificación ligera)
- ~5-10 notas/día × ~1000 tokens/nota = ~50K tokens/mes
- Cache evita re-clasificar notas sin cambios
