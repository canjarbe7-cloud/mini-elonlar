#!/usr/bin/env bash
set -euo pipefail

# Usage: run from the `elonlar` directory
# 1) Login to Heroku: `heroku login`
# 2) Run this script: `./deploy_heroku.sh my-app-name`

APP_NAME=${1:-}
if [ -z "$APP_NAME" ]; then
  echo "Usage: $0 <heroku-app-name>"
  exit 1
fi

git init 2>/dev/null || true
git add -A
git commit -m "Prepare for Heroku deployment" || true

# Create app if it doesn't exist
heroku apps:info -a "$APP_NAME" >/dev/null 2>&1 || heroku create "$APP_NAME"

# Set common config vars from .env (only if you already set them locally)
if [ -f .env ]; then
  echo "Pushing env vars from .env to Heroku (please review)"
  while IFS='=' read -r key val; do
    case "$key" in
      ''|#*) continue;;
    esac
    heroku config:set "$key=$val" -a "$APP_NAME"
  done < .env
fi

# Push code
git push heroku HEAD:main -f

# Run migrations and collectstatic
heroku run python manage.py migrate -a "$APP_NAME"
heroku run python manage.py collectstatic --noinput -a "$APP_NAME"

echo "Deployment complete. Open the app at: https://$APP_NAME.herokuapp.com"
