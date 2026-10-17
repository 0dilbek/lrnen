# VPS'ga joylash

Oddiy `systemd + Gunicorn + Nginx` usuli uchun [README_SYSTEMD.md](README_SYSTEMD.md) dan foydalaning. Quyidagi bo‘lim Docker Compose varianti uchun qoldirilgan.

Loyiha Docker Compose orqali ishlaydi: React build Nginx'da, Django esa ichki Docker tarmog'ida Gunicorn orqali ochiladi. Backend porti hostga chiqarilmagan; barcha API va media so'rovlari Nginx'dan o'tadi.

## Serverni tayyorlash

- VPS'ga Docker va Docker Compose o'rnating.
- Domenning `A` yozuvini VPS IP manziliga yo'naltiring.
- Firewall'da faqat SSH, 80 va 443 portlarini oching. 8000-portni ochmang.
- Loyiha bilan birga tayyor `db.sqlite3` va `static/` katalogini ko'chiring.
- Yuklangan fayllar uchun loyiha ildizida `media/` katalogi bo'lishi kerak.

```bash
mkdir -p media
cp .env.example .env
```

`.env` ichida kamida quyidagilarni almashtiring:

```env
SECRET_KEY=uzun-tasodifiy-maxfiy-kalit
DEBUG=False
ALLOWED_HOSTS=lms.example.com
CSRF_TRUSTED_ORIGINS=https://lms.example.com
CORS_ALLOWED_ORIGINS=https://lms.example.com
USE_X_ACCEL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

TLS tashqi reverse proxy yoki Cloudflare'da tugatilsa `SECURE_SSL_REDIRECT=False` qolishi mumkin. Django HTTPS'ni bevosita to'g'ri aniqlaydigan konfiguratsiyada `True` qilish mumkin.

## Ishga tushirish

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f backend
```

Backend har ishga tushganda migratsiyalarni va `collectstatic`ni avtomatik bajaradi. `db.sqlite3` va `media/` host kataloglari konteynerga bind mount qilingan, shuning uchun image qayta build qilinganda yo'qolmaydi.

Admin yaratish kerak bo'lsa:

```bash
docker compose exec backend python manage.py createsuperuser
```

## Media himoyasi

- `/media/...`, `/static/book/...`, `/static/book2/...`, `/static/book3/...` va `/static/audio/...` raw manzillari Nginx'da 404 qaytaradi.
- O'quvchiga faqat amal qilish muddati cheklangan imzolangan URL beriladi.
- Django URL'ni tekshiradi, fayl baytlarini esa samarali `X-Accel-Redirect` orqali Nginx uzatadi.
- Frontend download/context-menu/drag/PiP imkoniyatlarini cheklaydi va foydalanuvchi nomi bilan watermark chiqaradi.
- Brauzerga ko'rsatilgan materialni operatsion tizim yoki tashqi qurilma orqali 100% screenshot qilishni bloklashning universal usuli yo'q. Bu loyiha amaliy to'siqlar va foydalanuvchini aniqlovchi watermarkdan foydalanadi.

## Backup

Deploy va admin yuklashlaridan oldin muntazam nusxa oling:

```bash
cp db.sqlite3 "db.sqlite3.backup-$(date +%F-%H%M)"
tar -czf "media-backup-$(date +%F-%H%M).tar.gz" media/
```

SQLite backup paytida yozuvlar kelishi mumkin bo'lsa, avval `docker compose stop backend` qilib, backup tugagach `docker compose start backend` qiling.
