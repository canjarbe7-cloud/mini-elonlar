from django.conf import settings
from django.contrib.auth import get_user_model

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialApp


LOCAL_HOSTS = {"127.0.0.1", "localhost", "[::1]"}
LOCAL_ADDRS = {"127.0.0.1", "::1"}
GOOGLE_CLIENT_ID_SUFFIX = ".apps.googleusercontent.com"


def looks_like_google_client_id(value):
    return (value or "").strip().endswith(GOOGLE_CLIENT_ID_SUFFIX)


def app_has_google_credentials(app):
    return looks_like_google_client_id(app.client_id) and bool(app.secret.strip())


def has_google_oauth_credentials():
    if looks_like_google_client_id(settings.GOOGLE_CLIENT_ID) and settings.GOOGLE_CLIENT_SECRET:
        return True

    return any(
        app_has_google_credentials(app)
        for app in SocialApp.objects.filter(provider="google")
    )


def google_setup_allowed(request):
    host = request.get_host().split(":")[0]
    remote_addr = request.META.get("REMOTE_ADDR", "")
    return settings.DEBUG and (host in LOCAL_HOSTS or remote_addr in LOCAL_ADDRS)


def save_google_oauth(client_id, client_secret):
    if not looks_like_google_client_id(client_id):
        raise ValueError(
            "Google Client ID noto'g'ri. U odatda '.apps.googleusercontent.com' bilan tugaydi."
        )

    app = SocialApp.objects.filter(provider="google", provider_id="").first()
    created = app is None

    if created:
        app = SocialApp(provider="google", provider_id="")

    app.name = "Google"
    app.client_id = client_id
    app.secret = client_secret
    app.key = ""
    app.save()
    return app, created


def make_google_admin(email, username="admin"):
    email = email.strip().lower()
    username = username.strip()

    User = get_user_model()
    user, created = User.objects.get_or_create(username=username)
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True

    if created:
        user.set_unusable_password()

    user.save()
    EmailAddress.objects.update_or_create(
        user=user,
        email=email,
        defaults={"primary": True, "verified": True},
    )
    return user, created
