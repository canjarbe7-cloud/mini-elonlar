from django.core.management.base import BaseCommand, CommandError

from elonlar.auth_helpers import GOOGLE_CLIENT_ID_SUFFIX, looks_like_google_client_id, save_google_oauth


class Command(BaseCommand):
    help = "Google OAuth client ID va secret'ni allauth SocialApp sifatida saqlaydi."

    def add_arguments(self, parser):
        parser.add_argument("client_id")
        parser.add_argument("client_secret")

    def handle(self, *args, **options):
        client_id = options["client_id"].strip()
        client_secret = options["client_secret"].strip()

        if not client_id or not client_secret:
            raise CommandError("client_id va client_secret bo'sh bo'lmasligi kerak.")

        if not looks_like_google_client_id(client_id):
            raise CommandError(
                f"Google Client ID noto'g'ri. U {GOOGLE_CLIENT_ID_SUFFIX} bilan tugashi kerak."
            )

        app, created = save_google_oauth(client_id, client_secret)

        action = "yaratildi" if created else "yangilandi"
        self.stdout.write(self.style.SUCCESS(f"Google OAuth sozlamasi {action}: {app.client_id}"))
