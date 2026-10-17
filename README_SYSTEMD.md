# Systemd orqali VPS deploy

Bu variant Docker ishlatmaydi. Django `Gunicorn + systemd` orqali, frontend va himoyalangan media esa Nginx orqali ishlaydi.

## Bir buyruqda o‘rnatish

Avval lokal kompyuterdan loyiha, tayyor baza va static materiallarni xavfsiz yuboring:

```bash
SEED_DATA=1 bash deploy/rsync-to-vps.sh ubuntu@SERVER_IP /opt/english-lms
```

Bu birinchi deploy rejimi. U `db.sqlite3`ning yaxlit snapshotini ham yuboradi, ammo serverdagi `.env`ga tegmaydi va `--delete` ishlatmaydi. Keyingi kod yangilanishlarida `SEED_DATA=1`ni olib tashlang — shunda production bazasi va foydalanuvchi yuklagan media o‘zgarmaydi:

```bash
bash deploy/rsync-to-vps.sh ubuntu@SERVER_IP /opt/english-lms
```

Keyin VPS'ga kiring va loyiha katalogida quyidagini bajaring:

```bash
sudo APP_USER="$USER" LETSENCRYPT_EMAIL="admin@example.com" \
  bash deploy/install-systemd.sh lms.example.com
```

- `APP_USER` — loyiha fayllari bilan ishlaydigan oddiy Linux foydalanuvchisi.
- `LETSENCRYPT_EMAIL` berilsa Certbot HTTPS sertifikatini ham o‘rnatadi.
- DNS hali domenni VPS'ga yo‘naltirmagan bo‘lsa, `LETSENCRYPT_EMAIL` qismini vaqtincha olib tashlang va DNS tayyor bo‘lgach shu buyruqni yana ishlating.
- Skript mavjud `.env` ichidagi AI kalitlarini saqlaydi, production security qiymatlarini o‘zi yangilaydi.
- Tayyor `dist.tar.gz` ishlatiladi. Frontendni VPS'da qayta build qilish kerak bo‘lsa buyruqqa `BUILD_FRONTEND=1` qo‘shing.

## Bitta diagnostika buyrug‘i

```bash
sudo bash deploy/status-systemd.sh
```

U bir vaqtda systemd, Gunicorn socket, Nginx, frontend, backend API, Django, SQLite, disk, RAM va oxirgi loglarni tekshiradi. Barcha qatorlar `[OK]` bo‘lsa tizim sog‘lom.

## Kundalik boshqaruv

```bash
sudo systemctl status english-lms --no-pager
sudo systemctl restart english-lms
sudo systemctl reload nginx
sudo journalctl -u english-lms -f
```

Yangilanishdan keyin o‘rnatish buyrug‘ini qayta ishlatish mumkin: u dependency, migratsiya, static fayllar va servis konfiguratsiyasini yangilab restart qiladi.
