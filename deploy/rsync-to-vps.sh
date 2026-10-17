#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
REMOTE="${1:-}"
REMOTE_DIR="${2:-/opt/english-lms}"
SEED_DATA="${SEED_DATA:-0}"
DRY_RUN="${DRY_RUN:-0}"

usage() {
    printf 'Ishlatish:\n'
    printf '  Birinchi deploy: SEED_DATA=1 bash deploy/rsync-to-vps.sh user@server /opt/english-lms\n'
    printf '  Keyingi update:  bash deploy/rsync-to-vps.sh user@server /opt/english-lms\n'
    printf '  Sinov:           DRY_RUN=1 bash deploy/rsync-to-vps.sh user@server /opt/english-lms\n'
}

if [[ -z "$REMOTE" || ! "$REMOTE" =~ ^[A-Za-z0-9._-]+@[A-Za-z0-9._:-]+$ ]]; then
    printf 'Xato: user@server ko‘rsatilmagan yoki noto‘g‘ri.\n' >&2
    usage
    exit 1
fi
if [[ ! "$REMOTE_DIR" =~ ^/[A-Za-z0-9._/-]+$ ]]; then
    printf 'Xato: remote katalog absolut va bo‘sh joysiz bo‘lishi kerak.\n' >&2
    exit 1
fi
if ! command -v rsync >/dev/null 2>&1; then
    printf 'Xato: lokal kompyuterda rsync o‘rnatilmagan.\n' >&2
    exit 1
fi

printf 'Remote katalog tayyorlanmoqda: %s:%s\n' "$REMOTE" "$REMOTE_DIR"
ssh -t "$REMOTE" \
    "command -v rsync >/dev/null 2>&1 || { sudo apt-get update && sudo apt-get install -y rsync; }; sudo install -d -o \$(id -un) -g \$(id -gn) '$REMOTE_DIR'"

rsync_args=(
    --archive
    # Deploy root sifatida ishlatilganda lokal UID/GID production katalogining
    # egasi va www-data guruhini almashtirib yubormasin.
    --no-owner
    --no-group
    --compress
    --partial
    --human-readable
    --info=progress2
    --exclude=.git/
    --exclude=.claude/
    --exclude=.env
    --exclude=.venv/
    --exclude=myenv/
    --exclude=__pycache__/
    --exclude='*.pyc'
    --exclude='*.pyo'
    --exclude='*.log'
    --exclude=scratch/
    --exclude=staticfiles/
    --exclude=frontend/node_modules/
    --exclude=frontend/dist/
    --exclude='audio 1/'
    --exclude='book 1/'
    --exclude=pdf_images/
    --exclude=tmp_pages/
    --exclude=media/
    --exclude=db.sqlite3
    --exclude='*.pdf'
    --exclude='*.zip'
    --exclude='*.docx'
    --exclude=seed_book1_progress.json
    --exclude=seed_book2_progress.json
    --exclude=seed_book3_progress.json
)
if [[ "$DRY_RUN" == 1 ]]; then
    rsync_args+=(--dry-run)
fi

printf 'Loyiha kodi va static materiallar yuborilmoqda. .env/media/db himoyalangan.\n'
rsync "${rsync_args[@]}" "$APP_DIR/" "$REMOTE:$REMOTE_DIR/"

if [[ "$SEED_DATA" == 1 ]]; then
    snapshot_dir="$(mktemp -d)"
    trap 'rm -rf -- "$snapshot_dir"' EXIT
    snapshot_db="$snapshot_dir/db.sqlite3"
    python_bin="$APP_DIR/myenv/bin/python"
    [[ -x "$python_bin" ]] || python_bin="$(command -v python3)"

    "$python_bin" - "$APP_DIR/db.sqlite3" "$snapshot_db" <<'PY'
import sqlite3
import sys

source = sqlite3.connect(sys.argv[1])
destination = sqlite3.connect(sys.argv[2])
with destination:
    source.backup(destination)
result = destination.execute('PRAGMA integrity_check').fetchone()[0]
source.close()
destination.close()
if result != 'ok':
    raise SystemExit(f'SQLite snapshot xato: {result}')
print('SQLite snapshot: ok')
PY

    seed_args=(--archive --compress --partial --human-readable --info=progress2)
    if [[ "$DRY_RUN" == 1 ]]; then
        seed_args+=(--dry-run)
    fi
    printf 'Tayyor db.sqlite3 snapshot yuborilmoqda.\n'
    rsync "${seed_args[@]}" "$snapshot_db" "$REMOTE:$REMOTE_DIR/db.sqlite3"
    printf 'Boshlang‘ich media katalogi yuborilmoqda.\n'
    rsync "${seed_args[@]}" "$APP_DIR/media/" "$REMOTE:$REMOTE_DIR/media/"
fi

printf '\nRsync tugadi. --delete ishlatilmadi va serverdagi .env o‘zgarmadi.\n'
if [[ "$SEED_DATA" != 1 ]]; then
    printf 'db.sqlite3 va media/ ataylab yuborilmadi. Bu production ma’lumotlarini saqlaydi.\n'
fi
printf 'Keyingi qadam:\n'
printf '  ssh %s "cd %s && sudo env APP_USER=\$(id -un) bash deploy/install-systemd.sh DOMAIN"\n' "$REMOTE" "$REMOTE_DIR"
