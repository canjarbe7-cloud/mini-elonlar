import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from allauth.socialaccount.models import SocialAccount, SocialApp

from .models import Category, Listing


@override_settings(ALLOWED_HOSTS=["127.0.0.1", "testserver"], DEBUG=True)
class ListingViewsTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Elektronika")
        self.listing = Listing.objects.create(
            category=self.category,
            title="Test telefon",
            description="Yaxshi holatda",
            price=1200000,
            city="Toshkent",
            seller_name="Ali",
            phone="+998 90 000 00 00",
        )

    def test_home_page_shows_listing(self):
        response = self.client.get(reverse("elonlar:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.listing.title)

    def test_search_filters_listings(self):
        response = self.client.get(reverse("elonlar:home"), {"q": "telefon"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.listing.title)

    def test_category_filter_shows_matching_listings(self):
        furniture = Category.objects.create(name="Mebel")
        Listing.objects.create(
            category=furniture,
            title="Yangi stol",
            description="Ofis uchun",
            price=800000,
            city="Toshkent",
            seller_name="Hasan",
            phone="+998 90 222 22 22",
        )

        response = self.client.get(reverse("elonlar:home"), {"category": self.category.slug})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.listing.title)
        self.assertNotContains(response, "Yangi stol")

    def test_create_listing(self):
        response = self.client.post(
            reverse("elonlar:create"),
            {
                "category": self.category.pk,
                "title": "Yangi noutbuk",
                "description": "Ish uchun qulay",
                "price": "3500000",
                "city": "Samarqand",
                "address": "Markaz",
                "seller_name": "Vali",
                "phone": "+998 91 111 11 11",
                "condition": Listing.Condition.USED,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Listing.objects.filter(title="Yangi noutbuk").exists())

    def test_home_page_shows_listing_views(self):
        self.listing.views = 12
        self.listing.save(update_fields=["views"])

        response = self.client.get(reverse("elonlar:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "views-badge")
        self.assertContains(response, "12")

    def test_delete_list_requires_staff_login(self):
        response = self.client.get(reverse("elonlar:delete_list"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("admin:login")))

    def test_staff_user_can_delete_listing(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="admin",
            password="Admin12345!",
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.post(reverse("elonlar:delete", kwargs={"slug": self.listing.slug}))

        self.listing.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.listing.is_active)

    def test_login_page_renders_without_google_credentials(self):
        response = self.client.get(reverse("account_login"), HTTP_HOST="127.0.0.1:8000")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Google login hali sozlanmagan")
        self.assertContains(response, reverse("elonlar:google_setup"))

    def test_google_setup_page_saves_credentials_and_admin_email(self):
        User = get_user_model()

        response = self.client.post(
            reverse("elonlar:google_setup"),
            {
                "client_id": "1234567890-example.apps.googleusercontent.com",
                "client_secret": "test-secret",
                "admin_email": "owner@gmail.com",
                "admin_username": "owner",
            },
            HTTP_HOST="127.0.0.1:8000",
        )

        user = User.objects.get(username="owner")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.email, "owner@gmail.com")
        self.assertTrue(
            SocialApp.objects.filter(
                provider="google",
                client_id="1234567890-example.apps.googleusercontent.com",
            ).exists()
        )

    def test_google_setup_page_rejects_invalid_client_id(self):
        User = get_user_model()

        response = self.client.post(
            reverse("elonlar:google_setup"),
            {
                "client_id": "sanjar",
                "client_secret": "test-secret",
                "admin_email": "owner@gmail.com",
                "admin_username": "owner",
            },
            HTTP_HOST="127.0.0.1:8000",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="owner").exists())
        self.assertFalse(SocialApp.objects.filter(provider="google").exists())
        self.assertContains(response, ".apps.googleusercontent.com")

    def test_google_staff_user_can_reset_admin_password(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="googleadmin",
            email="admin@gmail.com",
            is_staff=True,
            is_superuser=True,
        )
        SocialAccount.objects.create(user=user, provider="google", uid="google-1")
        self.client.force_login(user)

        response = self.client.post(
            reverse("elonlar:admin_password"),
            {
                "new_password1": "NewAdmin12345!",
                "new_password2": "NewAdmin12345!",
            },
        )

        user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(user.check_password("NewAdmin12345!"))

    def test_non_staff_user_cannot_reset_admin_password(self):
        User = get_user_model()
        user = User.objects.create_user(username="simple", email="simple@gmail.com")
        SocialAccount.objects.create(user=user, provider="google", uid="google-2")
        self.client.force_login(user)

        response = self.client.get(reverse("elonlar:admin_password"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("elonlar:home"))

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_admin_can_reset_password_with_email_code(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="emailadmin",
            email="admin@gmail.com",
            password="OldAdmin12345!",
            is_staff=True,
            is_superuser=True,
        )

        response = self.client.post(
            reverse("elonlar:admin_password_request"),
            {"email": "admin@gmail.com"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("elonlar:admin_password_code"))
        self.assertEqual(len(mail.outbox), 1)

        code = re.search(r"\b\d{6}\b", mail.outbox[0].body).group(0)
        response = self.client.post(
            reverse("elonlar:admin_password_code"),
            {
                "code": code,
                "new_password1": "NewAdmin12345!",
                "new_password2": "NewAdmin12345!",
            },
        )

        user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("admin:login"))
        self.assertTrue(user.check_password("NewAdmin12345!"))

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_does_not_email_non_staff_user(self):
        User = get_user_model()
        User.objects.create_user(
            username="simple2",
            email="simple2@gmail.com",
            password="User12345!",
        )

        response = self.client.post(
            reverse("elonlar:admin_password_request"),
            {"email": "simple2@gmail.com"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

# Create your tests here.
