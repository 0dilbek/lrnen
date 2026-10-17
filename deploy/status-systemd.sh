#!/usr/bin/env bash
set -u

SERVICE_NAME="english-lms"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
PYTHON="$APP_DIR/.venv/bin/python"
DOMAIN="$(awk -F= '/^ALLOWED_HOSTS=/{split($2, hosts, ","); print hosts[1]; exit}' "$APP_DIR/.env" 2>/dev/null)"
DOMAIN="${DOMAIN:-localhost}"
APP_USER="$(systemctl show --property=User --value "$SERVICE_NAME" 2>/dev/null)"
APP_GROUP="$(systemctl show --property=Group --value "$SERVICE_NAME" 2>/dev/null)"
APP_GROUP="${APP_GROUP:-www-data}"
failed=0

check() {
    local label="$1"
    shift
    if "$@"; then
        printf '[OK]   %s\n' "$label"
    else
        printf '[FAIL] %s\n' "$label" >&2
        failed=1
    fi
}

printf 'English LMS system holati\n'
check 'systemd service active' systemctl is-active --quiet "$SERVICE_NAME"
check 'systemd service enabled' systemctl is-enabled --quiet "$SERVICE_NAME"
check 'nginx active' systemctl is-active --quiet nginx
check 'nginx konfiguratsiyasi' nginx -t
check 'Gunicorn socket' test -S /run/english-lms/gunicorn.sock
if [[ -n "$APP_USER" ]]; then
    check 'SQLite katalogiga Gunicorn yozishi' runuser -u "$APP_USER" -g "$APP_GROUP" -- test -w "$APP_DIR"
    check 'Media katalogiga Gunicorn yozishi' runuser -u "$APP_USER" -g "$APP_GROUP" -- test -w "$APP_DIR/media"
else
    printf '[FAIL] systemd servis foydalanuvchisi aniqlanmadi\n' >&2
    failed=1
fi
check 'Frontend HTTP 200' bash -c \
    "[[ \$(curl -L -sS -o /dev/null -w '%{http_code}' -H 'Host: $DOMAIN' http://127.0.0.1/) == 200 ]]"
check 'Backend API javobi' bash -c \
    "[[ \$(curl -L --post301 -sS -o /dev/null -w '%{http_code}' -H 'Host: $DOMAIN' -H 'Content-Type: application/json' -d '{}' http://127.0.0.1/api/auth/login/) == 400 ]]"

if [[ -x "$PYTHON" ]]; then
    check 'Django system check' "$PYTHON" "$APP_DIR/manage.py" check
    check 'SQLite integrity va ma’lumotlar' "$PYTHON" "$APP_DIR/manage.py" shell -c \
        "from django.db import connection; from courses.models import Lesson; from quiz.models import Exercise; c=connection.cursor(); c.execute('PRAGMA integrity_check'); ok=c.fetchone()[0]; print(f'DB={ok}; lessons={Lesson.objects.count()}; exercises={Exercise.objects.count()}'); raise SystemExit(ok != 'ok')"
else
    printf '[FAIL] Virtual environment topilmadi: %s\n' "$PYTHON" >&2
    failed=1
fi

printf '\nDisk va xotira:\n'
df -h "$APP_DIR" | tail -n 1
free -h | sed -n '1,2p'
printf '\nOxirgi service loglari:\n'
journalctl -u "$SERVICE_NAME" -n 20 --no-pager

exit "$failed"
