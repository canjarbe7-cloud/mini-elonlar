Deployment notes

This project is ready for deployment to services like Render or Railway.

Quick steps (Render / Railway):

1. Create a new GitHub repository and push this project.
2. On Render, create a new Python web service and link the GitHub repo.
3. The project includes `render.yaml` to configure Render deployment.
4. Set environment variables on Render before deploy:
   - `SECRET_KEY`
   - `DEBUG` (false)
   - `DJANGO_SETTINGS_MODULE` (default: `config.settings`)
   - `DATABASE_URL` (Postgres connection string) or leave empty to use SQLite (not recommended in production)
   - `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` (for Google SSO)
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME` (for Telegram login)
5. Build command: use the default Python build or the one from `render.yaml`.
6. Static files: whitenoise is enabled; run `python manage.py collectstatic --noinput` during deploy if Render doesn’t do it automatically.

If you want, I can prepare a GitHub repo and deploy to a free host if you provide access/authorization.
