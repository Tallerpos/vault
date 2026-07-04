---
fecha: 2026-07-04
tipo: idea
tags: []
relacionado: []
ai_tags: ["inteligencia-artificial", "automatización", "clasificación", "deepseek", "python"]
ai_category: miscelanea
ai_summary: 
ai_importance: 3
ai_key_topics: []
ai_classified_at: 2026-07-04T23:10:50.715439Z
---
# Idea: Sistema de clasificación automática con IA

Hoy implementé un sistema que usa DeepSeek API para clasificar notas automáticamente.

## Qué hace
- Detecta notas nuevas en el vault
- Envía el contenido a DeepSeek Flash API
- Clasifica con tags consistentes (sin duplicados)
- Actualiza el YAML con metadata AI
- Todo automático, cero intervención

## Por qué es importante
- Elimina la fricción de clasificar manualmente
- Tags consistentes (nunca crea duplicados como finanza vs economía)
- Costo mínimo (~/usr/bin/bash.30/mes para 100 notas/día)
- No intrusivo (campos con prefijo ai_)

## Tecnologías usadas
- DeepSeek Flash Cache API
- Python con watchdog
- inotifywait para detectar cambios
- YAML frontmatter con prefijo ai_
