# Elon

Oddiy Django marketplace loyihasi: e'lonlar ro'yxati, qidiruv, filterlar, e'lon qo'shish formasi va admin panel.

## Ishga tushirish

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Demo ma'lumot qo'shish:

```powershell
python manage.py seed_demo
```

Sayt: http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/

## Google login

Google OAuth ishlashi uchun Google Cloud Console'da OAuth Client ID yarating va redirect URI sifatida quyidagini qo'shing:

```text
http://127.0.0.1:8000/accounts/google/login/callback/
```

Keyin credential'larni ikki usuldan biri bilan kiriting:

```powershell
$env:GOOGLE_CLIENT_ID="client-id"
$env:GOOGLE_CLIENT_SECRET="client-secret"
python manage.py runserver
```

Yoki admin panelda `Social applications` bo'limidan Google app yarating.

Sayt orqali sozlash:

```text
http://127.0.0.1:8000/google-sozlash/
```

Command orqali saqlash:

```powershell
python manage.py setup_google_oauth "client-id" "client-secret"
```

Admin parol esdan chiqsa, Google email'ni admin akkauntga ulang:

```powershell
python manage.py make_google_admin "sizning@gmail.com"
```

So'ng Google orqali kiring va `/admin-parol/` sahifasida yangi admin parol qo'ying.

## Admin parolni Gmail kodi bilan tiklash

Admin akkauntning `email` maydonida Gmail manzil bo'lsa, login sahifasidagi `Parolni tiklash` havolasi orqali 6 xonali kod yuboriladi. Kod 10 daqiqa amal qiladi.

Lokal testda kod terminalga chiqadi. Haqiqiy Gmailga yuborish uchun `.env` faylga SMTP sozlamalarini qo'shing:

```powershell
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=sizning@gmail.com
EMAIL_HOST_PASSWORD=google-app-password
DEFAULT_FROM_EMAIL=sizning@gmail.com
```

Gmail oddiy parolni qabul qilmaydi; Google akkauntingizdan App Password yaratib `EMAIL_HOST_PASSWORD` ga qo'ying.
