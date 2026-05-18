from django.db.utils import OperationalError, ProgrammingError
from django.conf import settings

from .auth_helpers import google_setup_allowed, has_google_oauth_credentials


def google_auth(request):
    try:
        ready = has_google_oauth_credentials()
    except (OperationalError, ProgrammingError):
        ready = False

    telegram_ready = bool(getattr(settings, "TELEGRAM_BOT_TOKEN", "") and getattr(settings, "TELEGRAM_BOT_USERNAME", ""))

    return {
        "google_auth_ready": ready,
        "google_setup_allowed": google_setup_allowed(request),
        "telegram_bot_ready": telegram_ready,
        "telegram_bot_username": getattr(settings, "TELEGRAM_BOT_USERNAME", ""),
    }
