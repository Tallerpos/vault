#!/bin/bash
# AI Watcher v5.0 — Bulletproof Edition
# 
# Mejoras vs v4.0:
# - Debounce real con deduplicación
# - Filtro de placeholders y notas vacías
# - Lock file para coordinación con vault-watcher
# - Retry queue periódico
# - Mejor manejo de permisos
#
set -euo pipefail

VAULT_DIR="/opt/vault/Sync"
CLASSIFIER="/opt/vault/Sync/.ai-classifier/classifier.py"
HASH_DIR="/opt/vault/Sync/.ai-classifier/cache/hashes"
LOG_FILE="/opt/vault/Sync/.ai-classifier/logs/watcher.log"
DEBOUNCE=45
QUEUE_FILE="/tmp/ai-watcher-queue.$$"
LOCK_FILE="/tmp/ai-classifier.lock"
CLASSIFY_COUNTER=0

mkdir -p "$HASH_DIR" "$(dirname "$LOG_FILE")"

# ── Logging ──────────────────────────────────────────────
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }

# ── Hash change detection (body-only) ─────────────────────
# IMPORTANTE: Hashea solo el body (sin frontmatter) para que cambios
# en campos ai_* NO vuelvan a disparar clasificación.
get_body_hash() {
    # Extraer todo después del primer ---\n...\n--- block
    awk 'BEGIN{skip=1} /^---$/ {if(skip){skip=0; next}} !skip' "$1" 2>/dev/null | sha256sum | awk '{print $1}'
}

file_changed() {
    local file="$1"
    local hash_file="$HASH_DIR/$(echo "$file" | sha256sum | awk '{print $1}')"
    local current_hash
    current_hash=$(get_body_hash "$file")
    
    if [ -z "$current_hash" ]; then
        return 1  # No se pudo hashear, skip
    fi
    if [ -f "$hash_file" ] && [ "$current_hash" = "$(cat "$hash_file" 2>/dev/null)" ]; then
        return 1  # No cambió
    fi
    echo "$current_hash" > "$hash_file"
    return 0  # Sí cambió
}

# ── Filtros inteligentes ─────────────────────────────────
should_skip_file() {
    local file="$1"
    local basename
    basename=$(basename "$file")
    local name_lower
    name_lower=$(echo "$basename" | tr '[:upper:]' '[:lower:]')
    
    # No es markdown
    [[ "$file" != *.md ]] && return 0
    
    # Nombres que siempre ignoramos
    [[ "$name_lower" == sin\ título* ]] && return 0
    [[ "$name_lower" == sin\ titulo* ]] && return 0
    [[ "$name_lower" == untitled* ]] && return 0
    [[ "$name_lower" == config.md ]] && return 0
    [[ "$name_lower" == sistema-ai.md ]] && return 0
    [[ "$name_lower" == guia_recuperacion.md ]] && return 0
    [[ "$name_lower" == enlaces.md ]] && return 0
    
    # Archivo vacío o solo placeholder
    local body
    body=$(sed -n '/^---$/,/^---$/!p' "$file" 2>/dev/null | tr -d '[:space:]')
    if [ -z "$body" ] || [ "$body" = "Escribeaquítunota." ] || [ "$body" = "Escribeaquitunota." ]; then
        return 0
    fi
    
    # Body demasiado corto (menos de 20 chars útiles)
    local body_len=${#body}
    [ "$body_len" -lt 20 ] && return 0
    
    return 1  # NO skip, procesar
}

# ── Clasificación de archivo ─────────────────────────────
classify_file() {
    local file="$1"
    
    # Filtrar
    if should_skip_file "$file"; then
        log "SKIPPED (filter): $file"
        return
    fi
    
    # Arreglar permisos proactivamente
    sudo chown abner:abner "$file" 2>/dev/null || true
    
    # Verificar cambio real
    if ! file_changed "$file"; then
        log "SKIPPED (no change): $file"
        return
    fi
    
    # Señalizar: clasificando (vault-watcher espera)
    touch "$LOCK_FILE"
    
    log "PROCESSING: $file"
    local result
    result=$(python3 "$CLASSIFIER" "$file" 2>&1) || true
    echo "$result" | while IFS= read -r line; do log "  $line"; done
    
    # Parsear resultado
    local status
    status=$(echo "$result" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('status', 'unknown'))
except:
    print('unknown')
" 2>/dev/null) || status="unknown"
    
    case "$status" in
        success)
            local tags related
            tags=$(echo "$result" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(', '.join(data.get('tags', [])))
except:
    print('?')
" 2>/dev/null) || tags="?"
            related=$(echo "$result" | python3 -c "
import sys, json
try:
    print(json.load(sys.stdin).get('related_count', 0))
except:
    print(0)
" 2>/dev/null) || related="0"
            log "✅ SUCCESS [$tags] related=$related"
            ;;
        skipped)
            log "SKIPPED (classifier decision)"
            ;;
        *)
            log "❌ ERROR: $file (status=$status)"
            ;;
    esac
    
    # Liberar lock
    rm -f "$LOCK_FILE"
}

# ── Retry queue periódico ────────────────────────────────
process_retries() {
    log "Processing retry queue..."
    local result
    result=$(python3 "$CLASSIFIER" --retry 2>&1) || true
    echo "$result" | while IFS= read -r line; do log "  RETRY: $line"; done
}

# ── Cleanup ──────────────────────────────────────────────
cleanup() {
    rm -f "$LOCK_FILE" "$QUEUE_FILE" 2>/dev/null
    log "AI Watcher stopped."
}
trap cleanup EXIT

# ── Main ─────────────────────────────────────────────────
log "AI Watcher v5.0 started..."

# Fix permisos globales al inicio
sudo chown -R abner:abner "$VAULT_DIR" 2>/dev/null || true

inotifywait -m -r "$VAULT_DIR" \
    --exclude '\.(git|optimizer|silverbullet|ai-classifier|tag-registry)|Templates/' \
    -e close_write -e moved_to \
    --format '%w%f' |
while read -r file; do
    [[ "$file" != *.md ]] && continue
    
    # Escribir a queue file para deduplicar
    echo "$file" >> "$QUEUE_FILE"
    
    # Debounce: esperar a que se consoliden los cambios
    sleep $DEBOUNCE
    
    # Drenar TODOS los eventos pendientes del pipe (timeout 2s)
    while read -r -t 2 additional; do
        [[ "$additional" == *.md ]] && echo "$additional" >> "$QUEUE_FILE"
    done
    
    # Deduplicar y procesar
    if [ -f "$QUEUE_FILE" ]; then
        mapfile -t unique_files < <(sort -u "$QUEUE_FILE")
        > "$QUEUE_FILE"  # Limpiar queue
        
        for f in "${unique_files[@]}"; do
            [ -f "$f" ] && classify_file "$f"
        done
    fi
    
    # Retry queue cada 5 ciclos
    CLASSIFY_COUNTER=$((CLASSIFY_COUNTER + 1))
    if [ $((CLASSIFY_COUNTER % 5)) -eq 0 ]; then
        process_retries
    fi
done
