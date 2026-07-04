#!/bin/bash
VAULT_DIR="/opt/vault/Sync"
source /etc/environment
CLASSIFIER="/opt/vault/Sync/.ai-classifier/classifier.py"
HASH_DIR="/opt/vault/Sync/.ai-classifier/cache/hashes"
LOG_FILE="/opt/vault/Sync/.ai-classifier/logs/watcher.log"
DEBOUNCE=60

mkdir -p "$HASH_DIR" "$(dirname $LOG_FILE)"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

get_hash() {
    sha256sum "$1" | awk '{print $1}'
}

file_changed() {
    local file="$1"
    local hash_file="$HASH_DIR/$(echo "$file" | sha256sum | awk '{print $1}')"
    local current_hash=$(get_hash "$file")
    if [ -f "$hash_file" ]; then
        local stored_hash=$(cat "$hash_file")
        if [ "$current_hash" = "$stored_hash" ]; then
            return 1
        fi
    fi
    echo "$current_hash" > "$hash_file"
    return 0
}

log "AI Watcher started..."

inotifywait -m -r "$VAULT_DIR" \
    --exclude '\.git|\.optimizer|\.silverbullet|\.ai-classifier|\.tag-registry' \
    -e close_write -e moved_to \
    --format '%w%f' |
while read -r file; do
    [[ "$file" != *.md ]] && continue
    sleep $DEBOUNCE
    while read -r -t 0.1 additional; do
        file="$additional"
    done
    if ! file_changed "$file"; then
        log "SKIPPED (no change): $file"
        continue
    fi
    log "PROCESSING: $file"
    sudo python3 "$CLASSIFIER" "$file" 2>&1 | while read -r line; do
        log "  $line"
    done
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log "SUCCESS: $file"
    else
        log "ERROR: $file"
    fi
done
