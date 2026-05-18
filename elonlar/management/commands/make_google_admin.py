from django.core.management.base import BaseCommand, CommandError

from elonlar.auth_helpers import make_google_admin


class Command(BaseCommand):
    help = "Google email'ni admin akkauntga ulash uchun staff/superuser qilib tayyorlaydi."

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("--username", default="admin")

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        username = options["username"].strip()

        if not email or "@" not in email:
            raise CommandError("To'g'ri email kiriting. Masalan: user@gmail.com")

        if not username:
            raise CommandError("Username bo'sh bo'lmasligi kerak.")

        user, created = make_google_admin(email, username)

        action = "yaratildi" if created else "yangilandi"
        self.stdout.write(self.style.SUCCESS(f"{username} admin {action}: {email}"))
