# Vercel Deployment Guide

## Muammoni bartaraf etish

**Xatolik:** `unable to open database file` - Vercel'da SQLite fayllar saqlanmaydi.

**Yechim:** PostgreSQL cloud database ishlatish.

## O'rnatish

### 1️⃣ PostgreSQL bazani yaratish

Quyidagidan birini tanlang:

- **Neon** (Tavsiya): https://console.neon.tech
- **Railway**: https://railway.app
- **Render**: https://render.com
- **Supabase**: https://supabase.com

### 2️⃣ .env.production faylini Vercel'da o'rnatish

Vercel Dashboard → Settings → Environment Variables

```
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.vercel.app
```

### 3️⃣ Vercel'ga push qilish

```bash
git add .
git commit -m "Vercel uchun Django konfiguratsiyasi"
git push origin main
```

Vercel avtomatik o'rnatadi va deploy qiladi.

### 4️⃣ Admin foydalanuvchisini yaratish

Deploy qilgandan keyin:

```bash
vercel env pull  # .env.local'ni yuklab olish
python manage.py createsuperuser
```

## Local'da test qilish

```bash
# .env faylini yarating
cp .env.example .env

# PostgreSQL'ni local'da o'rnatish (yoki containerda)
# Keyin:

python manage.py migrate
python manage.py runserver
```

## Muammolar

**"Static files topilmadi"** → Vercel deploy qilgandan keyin `python manage.py collectstatic --noinput` avtomatik ishga tushuriladi.

**"Media fayllar yadini o'tqazmoqda"** → Vercel ephemeral filesystem ishlatadi. Media fayllar uchun S3 yoki boshqa storage serbisdan foydalaning.
