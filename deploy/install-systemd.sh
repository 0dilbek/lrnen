#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE_NAME="english-lms"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
DOMAIN="${1:-}"
APP_USER="${APP_USER:-${SUDO_USER:-}}"

usage() {
    printf 'Ishlatish: sudo [APP_USER=user] [LETSENCRYPT_EMAIL=email] bash deploy/install-systemd.sh lms.example.com\n'
}

if [[ $EUID -ne 0 ]]; then
    printf 'Xato: bu skript sudo/root bilan ishlatiladi.\n' >&2
    usage
    exit 1
fi
if [[ -z "$DOMAIN" || ! "$DOMAIN" =~ ^([A-Za-z0-9][A-Za-z0-9.-]*|[0-9]{1,3}(\.[0-9]{1,3}){3})$ ]]; then
    printf 'Xato: domen yoki server IP manzilini birinchi argument sifatida kiriting.\n' >&2
    usage
    exit 1
fi

if [[ "$DOMAIN" =~ ^[0-9.]+$ ]]; then
    server_names="$DOMAIN"
    allowed_hosts="$DOMAIN,localhost,127.0.0.1"
    trusted_origins="http://$DOMAIN"
else
    server_names="$DOMAIN www.$DOMAIN"
    allowed_hosts="$DOMAIN,www.$DOMAIN,localhost,127.0.0.1"
    trusted_origins="https://$DOMAIN,https://www.$DOMAIN"
fi
if [[ -z "$APP_USER" || "$APP_USER" == root ]] || ! id "$APP_USER" >/dev/null 2>&1; then
    printf 'Xato: servis uchun root bo‘lmagan APP_USER kerak. Masalan:\n' >&2
    printf '  sudo APP_USER=ubuntu bash deploy/install-systemd.sh %s\n' "$DOMAIN" >&2
    exit 1
fi
if [[ "$APP_DIR" =~ [[:space:]] ]]; then
    printf 'Xato: loyiha yo‘lida bo‘sh joy bo‘lmasligi kerak: %s\n' "$APP_DIR" >&2
    exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3 python3-venv python3-pip nginx curl openssl

if [[ ! -d "$APP_DIR/.venv" ]]; then
    python3 -m venv "$APP_DIR/.venv"
fi
"$APP_DIR/.venv/bin/pip" install --upgrade pip wheel
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

if [[ "${BUILD_FRONTEND:-0}" == 1 ]]; then
    command -v npm >/dev/null 2>&1 || {
        printf 'Xato: BUILD_FRONTEND=1 uchun Node.js/npm o‘rnatilgan bo‘lishi kerak.\n' >&2
        exit 1
    }
    npm --prefix "$APP_DIR/frontend" ci
    npm --prefix "$APP_DIR/frontend" run build
elif [[ -f "$APP_DIR/dist.tar.gz" ]]; then
    # The archive is produced as `tar -C frontend dist`, so it already
    # contains the top-level dist/ directory.
    install -d "$APP_DIR/frontend"
    tar -xzf "$APP_DIR/dist.tar.gz" -C "$APP_DIR/frontend"
    if [[ ! -f "$APP_DIR/frontend/dist/index.html" ]]; then
        printf 'Xato: dist.tar.gz ichida dist/index.html topilmadi.\n' >&2
        exit 1
    fi
elif [[ ! -f "$APP_DIR/frontend/dist/index.html" ]]; then
    printf 'Xato: dist.tar.gz ham, frontend/dist/index.html ham topilmadi.\n' >&2
    exit 1
fi

touch "$APP_DIR/.env"
upsert_env() {
    local key="$1" value="$2" temporary
    temporary="$(mktemp)"
    awk -v key="$key" -v value="$value" '
        BEGIN { replaced = 0 }
        $0 ~ "^" key "=" { print key "=" value; replaced = 1; next }
        { print }
        END { if (!replaced) print key "=" value }
    ' "$APP_DIR/.env" > "$temporary"
    cat "$temporary" > "$APP_DIR/.env"
    rm -f "$temporary"
}

current_secret="$(awk -F= '/^SECRET_KEY=/{sub(/^SECRET_KEY=/, ""); print; exit}' "$APP_DIR/.env")"
if [[ ${#current_secret} -lt 50 || "$current_secret" == django-insecure-* ]]; then
    upsert_env SECRET_KEY "$(openssl rand -hex 48)"
fi
upsert_env DEBUG False
upsert_env ALLOWED_HOSTS "$allowed_hosts"
upsert_env CSRF_TRUSTED_ORIGINS "$trusted_origins"
upsert_env CORS_ALLOWED_ORIGINS "$trusted_origins"
upsert_env USE_X_ACCEL_REDIRECT True
upsert_env SESSION_COOKIE_SECURE True
upsert_env CSRF_COOKIE_SECURE True
upsert_env SECURE_SSL_REDIRECT False
upsert_env SECURE_HSTS_SECONDS 0

install -d -o "$APP_USER" -g www-data -m 0750 "$APP_DIR/media"
# Old deploy/admin commands may have created nested upload directories as root.
# Gunicorn must own every directory so Django can save new audio/video/image files.
chown -R "$APP_USER":www-data "$APP_DIR/media"
find "$APP_DIR/media" -type d -exec chmod 0750 {} +
find "$APP_DIR/media" -type f -exec chmod 0640 {} +
touch "$APP_DIR/db.sqlite3"
chown "$APP_USER":www-data "$APP_DIR/db.sqlite3"
chmod 0660 "$APP_DIR/db.sqlite3"
# SQLite creates its journal/WAL beside db.sqlite3. Making only the database
# file writable is not enough: Gunicorn must also be able to write APP_DIR.
chown "$APP_USER":www-data "$APP_DIR"
chmod 0770 "$APP_DIR"
chown root:www-data "$APP_DIR/.env"
chmod 0640 "$APP_DIR/.env"

if ! runuser -u "$APP_USER" -g www-data -- test -w "$APP_DIR"; then
    printf 'Xato: %s foydalanuvchisi SQLite katalogiga yoza olmaydi: %s\n' "$APP_USER" "$APP_DIR" >&2
    exit 1
fi
if ! runuser -u "$APP_USER" -g www-data -- test -w "$APP_DIR/media"; then
    printf 'Xato: %s foydalanuvchisi media katalogiga yoza olmaydi: %s/media\n' "$APP_USER" "$APP_DIR" >&2
    exit 1
fi

"$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" migrate --noinput
"$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" collectstatic --noinput
"$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" check
chmod -R a+rX "$APP_DIR/frontend/dist" "$APP_DIR/staticfiles" "$APP_DIR/static"
if ! runuser -u www-data -- test -r "$APP_DIR/frontend/dist/index.html"; then
    printf 'Xato: Nginx loyiha katalogiga kira olmaydi. Loyihani /opt/english-lms yoki /var/www/english-lms ichiga ko‘chiring.\n' >&2
    exit 1
fi

escape_sed() {
    printf '%s' "$1" | sed 's/[&|]/\\&/g'
}
escaped_dir="$(escape_sed "$APP_DIR")"
escaped_user="$(escape_sed "$APP_USER")"
escaped_server_names="$(escape_sed "$server_names")"

sed \
    -e "s|__APP_DIR__|$escaped_dir|g" \
    -e "s|__APP_USER__|$escaped_user|g" \
    "$APP_DIR/deploy/systemd/english-lms.service.template" \
    > "/etc/systemd/system/$SERVICE_NAME.service"

sed \
    -e "s|__APP_DIR__|$escaped_dir|g" \
    -e "s|__SERVER_NAMES__|$escaped_server_names|g" \
    "$APP_DIR/deploy/nginx/english-lms.conf.template" \
    > "/etc/nginx/sites-available/$SERVICE_NAME"
ln -sfn "/etc/nginx/sites-available/$SERVICE_NAME" "/etc/nginx/sites-enabled/$SERVICE_NAME"
rm -f /etc/nginx/sites-enabled/default

systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME"
nginx -t
systemctl enable --now nginx
systemctl reload nginx

site_scheme=http
if [[ -n "${LETSENCRYPT_EMAIL:-}" && ! "$DOMAIN" =~ ^[0-9.]+$ ]]; then
    apt-get install -y certbot python3-certbot-nginx
    certbot --nginx --non-interactive --agree-tos --redirect \
        --email "$LETSENCRYPT_EMAIL" -d "$DOMAIN"
    upsert_env SECURE_HSTS_SECONDS 31536000
    systemctl restart "$SERVICE_NAME"
    site_scheme=https
fi

printf '\nSystemd deploy tayyor.\n'
printf 'Sayt: %s://%s\n' "$site_scheme" "$DOMAIN"
printf 'Holat: sudo bash %s/deploy/status-systemd.sh\n' "$APP_DIR"
if [[ -z "${LETSENCRYPT_EMAIL:-}" ]]; then
    printf 'HTTPS hali o‘rnatilmadi. DNS tayyor bo‘lgach LETSENCRYPT_EMAIL bilan skriptni qayta ishlating.\n'
fi
