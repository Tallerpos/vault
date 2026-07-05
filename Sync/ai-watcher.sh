#!/bin/bash
VAULT_DIR="/opt/vault/Sync"
# source /etc/environment (moved to systemd EnvironmentFile)
CLASSIFIER="/opt/vault/Sync/.ai-classifier/classifier.py"
HASH_DIR="/opt/vault/Sync/.ai-classifier/cache/hashes"
LOG_FILE="/opt/vault/Sync/.ai-classifier/logs/watcher.log"
DEBOUNCE=60

mkdir -p "$HASH_DIR" "$(dirname "$LOG_FILE")"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }
get_hash() { sha256sum "$1" | awk '{print $1}'; }
file_changed() {
    local file="$1"
    local hf="$HASH_DIR/$(echo "$file" | sha256sum | awk '{print $1}')"
    local ch=$(get_hash "$file")
    [ -f "$hf" ] && [ "$ch" = "$(cat "$hf")" ] && return 1
    echo "$ch" > "$hf"; return 0
}

log "AI Watcher v3.0 started..."
inotifywait -m -r "$VAULT_DIR" \
    --exclude '\.(git|optimizer|silverbullet|ai-classifier|tag-registry)|Templates/' \
    -e close_write -e moved_to \
    --format '%w%f' |
while read -r file; do
    [[ "$file" != *.md ]] && continue
    sleep $DEBOUNCE
    while read -r -t 0.1 additional; do file="$additional"; done
    sudo chown abner:abner "$file" 2>/dev/null
    if ! file_changed "$file"; then log "SKIPPED (no change): $file"; continue; fi
    log "PROCESSING: $file"
    result=$(python3 "$CLASSIFIER" "$file" 2>&1)
    echo "$result" | while read -r line; do log "  $line"; done
    status=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null)
    if [ "$status" = "success" ]; then
        tags=$(echo "$result" | python3 -c "import sys,json; print(', '.join(json.load(sys.stdin).get('tags',[])))" 2>/dev/null)
        log "SUCCESS [$tags]"
    elif [ "$status" = "skipped" ]; then log "SKIPPED (no changes detected)"
    else log "ERROR: $file"; fi
done
