Deployment notes

This project is ready for deployment to services like Render or Railway.

Quick steps (Render / Railway):

1. Create a new GitHub repository and push this project.
2. On the hosting service, create a new web service and link the GitHub repo.
3. Set environment variables on the host:
   - `SECRET_KEY`
   - `DEBUG` (false)
   - `DJANGO_SETTINGS_MODULE` (if needed, default is `config.settings`)
   - `DATABASE_URL` (Postgres connection string) or leave empty to use SQLite (not recommended in production)
   - `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` (for Google SSO)
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME` (for Telegram login)
4. Build command: use default Python build. The `Procfile` runs `gunicorn`.
5. Static files: whitenoise is enabled; run `python manage.py collectstatic --noinput` during deploy if the host doesn't run migrations automatically.

If you want, I can prepare a GitHub repo and deploy to a free host if you provide access/authorization.
