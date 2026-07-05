#!/usr/bin/env python3
"""Health Check — System status monitor.

Checks:
- Service status (ai-watcher, vault-watcher)
- Unclassified notes
- Recent errors in logs
- Retry queue status
- File permissions
- Disk usage

Usage:
    python3 health_check.py
    python3 classifier.py --health
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta

VAULT = Path('/opt/vault/Sync')
LOG_DIR = VAULT / '.ai-classifier/logs'
CLASSIFIER_LOG = LOG_DIR / 'classifier.log'
WATCHER_LOG = LOG_DIR / 'watcher.log'
REGISTRY = VAULT / '.tag-registry.json'
RETRY_QUEUE = VAULT / '.ai-classifier/cache/retry_queue.json'


def check_health():
    """Run all health checks. Returns number of issues found."""
    issues = []
    warnings = []
    stats = {}

    # 1. Services running
    for svc in ['ai-watcher', 'vault-watcher']:
        try:
            r = subprocess.run(
                ['systemctl', 'is-active', svc],
                capture_output=True, text=True, timeout=5
            )
            if r.stdout.strip() != 'active':
                issues.append(f'🔴 Servicio {svc} NO activo (estado: {r.stdout.strip()})')
            else:
                stats[svc] = 'active'
        except Exception as e:
            issues.append(f'🔴 No se puede verificar {svc}: {e}')

    # 2. Unclassified notes
    unclassified = []
    total_notes = 0
    classified_notes = 0
    for md in VAULT.rglob('*.md'):
        if any(p.startswith('.') or p == 'Templates' for p in md.parts):
            continue
        if not md.is_file():
            continue
        total_notes += 1
        try:
            content = md.read_text(encoding='utf-8')
            if 'ai_classified_at:' in content:
                classified_notes += 1
            else:
                name = md.stem.lower()
                # Solo reportar notas que deberían estar clasificadas
                skip = ('sin título', 'sin titulo', 'untitled', 'config',
                        'sistema-ai', 'guia_recuperacion', 'enlaces')
                if not any(name.startswith(s) for s in skip):
                    unclassified.append(md.name)
        except Exception:
            continue

    stats['total_notes'] = total_notes
    stats['classified'] = classified_notes
    if unclassified:
        warnings.append(
            f'🟡 {len(unclassified)} notas sin clasificar: '
            f'{", ".join(unclassified[:5])}'
        )

    # 3. Recent errors in classifier log
    if CLASSIFIER_LOG.exists():
        recent_errors = 0
        cutoff = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H')
        try:
            for line in CLASSIFIER_LOG.read_text().splitlines()[-100:]:
                if 'ERROR' in line and cutoff in line:
                    recent_errors += 1
            if recent_errors > 0:
                warnings.append(
                    f'🟠 {recent_errors} errores en la última hora '
                    f'(ver classifier.log)'
                )
        except Exception:
            pass

    # 4. Retry queue
    if RETRY_QUEUE.exists():
        try:
            queue = json.loads(RETRY_QUEUE.read_text())
            if queue:
                warnings.append(
                    f'🟡 {len(queue)} notas en cola de reintentos'
                )
                stats['retry_queue'] = len(queue)
        except Exception:
            pass

    # 5. File permissions
    perm_issues = 0
    for md in VAULT.rglob('*.md'):
        if any(p.startswith('.') for p in md.parts):
            continue
        if not os.access(md, os.W_OK):
            perm_issues += 1
    if perm_issues > 0:
        issues.append(
            f'🔴 {perm_issues} archivos sin permisos de escritura'
        )

    # 6. Tag registry health
    if REGISTRY.exists():
        try:
            reg = json.loads(REGISTRY.read_text())
            stats['tags'] = len(reg.get('tags', {}))
            stats['examples'] = len(reg.get('successful_examples', []))
            stats['corrections'] = len(reg.get('corrections', []))
        except Exception:
            warnings.append('🟠 Tag registry no se puede leer')

    # 7. Disk usage
    try:
        r = subprocess.run(
            ['du', '-sh', str(VAULT)],
            capture_output=True, text=True, timeout=5
        )
        stats['vault_size'] = r.stdout.split()[0] if r.stdout else 'unknown'
    except Exception:
        pass

    # Output
    print('=' * 50)
    print('  VAULT AI SYSTEM — HEALTH CHECK')
    print('=' * 50)

    if not issues and not warnings:
        print('\n✅ Sistema completamente saludable\n')
    else:
        if issues:
            print('\n--- PROBLEMAS CRÍTICOS ---')
            for i in issues:
                print(f'  {i}')
        if warnings:
            print('\n--- ADVERTENCIAS ---')
            for w in warnings:
                print(f'  {w}')

    print('\n--- ESTADÍSTICAS ---')
    for k, v in stats.items():
        print(f'  {k}: {v}')
    print()

    return len(issues)


if __name__ == '__main__':
    sys.exit(check_health())
