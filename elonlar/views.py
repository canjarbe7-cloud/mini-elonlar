import hashlib
import hmac
import secrets
import time
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from allauth.socialaccount.models import SocialAccount

from .auth_helpers import google_setup_allowed, make_google_admin, save_google_oauth
from .forms import AdminPasswordCodeForm, AdminPasswordResetRequestForm, GoogleSetupForm, ListingForm
from .models import Category, Listing


ADMIN_RESET_SESSION_KEY = "admin_password_reset"
ADMIN_RESET_TTL_MINUTES = 10


def _admin_reset_code_hash(code):
    value = f"{settings.SECRET_KEY}:{code}".encode()
    return hashlib.sha256(value).hexdigest()


def _get_admin_by_email(email):
    User = get_user_model()
    return User.objects.filter(email__iexact=email, is_staff=True, is_active=True).first()


def listing_list(request):
    listings = Listing.objects.filter(is_active=True).select_related("category")
    categories = Category.objects.all()

    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    city = request.GET.get("city", "").strip()
    price_min = request.GET.get("price_min", "").strip()
    price_max = request.GET.get("price_max", "").strip()
    sort = request.GET.get("sort", "new").strip()

    if query:
        listings = listings.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(city__icontains=query)
            | Q(category__name__icontains=query)
        )

    if category_slug:
        listings = listings.filter(category__slug=category_slug)

    if city:
        listings = listings.filter(city=city)

    try:
        if price_min:
            listings = listings.filter(price__gte=Decimal(price_min))
        if price_max:
            listings = listings.filter(price__lte=Decimal(price_max))
    except InvalidOperation:
        messages.warning(request, "Narx filterida faqat raqam kiriting.")

    sort_options = {
        "new": "-created_at",
        "cheap": "price",
        "expensive": "-price",
        "popular": "-views",
    }
    listings = listings.order_by(sort_options.get(sort, "-created_at"))

    paginator = Paginator(listings, 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    page_query = request.GET.copy()
    page_query.pop("page", None)

    context = {
        "page_obj": page_obj,
        "categories": categories,
        "cities": Listing.CITY_CHOICES,
        "filters": {
            "q": query,
            "category": category_slug,
            "city": city,
            "price_min": price_min,
            "price_max": price_max,
            "sort": sort,
        },
        "page_query": page_query.urlencode(),
        "total_count": listings.count(),
    }
    return render(request, "elonlar/home.html", context)


def listing_detail(request, slug):
    listing = get_object_or_404(
        Listing.objects.select_related("category"),
        slug=slug,
        is_active=True,
    )
    Listing.objects.filter(pk=listing.pk).update(views=F("views") + 1)
    listing.views += 1
    similar_listings = (
        Listing.objects.filter(category=listing.category, is_active=True)
        .exclude(pk=listing.pk)
        .select_related("category")[:3]
    )
    return render(
        request,
        "elonlar/detail.html",
        {"listing": listing, "similar_listings": similar_listings},
    )


def listing_create(request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save()
            messages.success(request, "E'loningiz saytga qo'shildi.")
            return redirect(listing.get_absolute_url())
    else:
        form = ListingForm()

    return render(request, "elonlar/qoshish.html", {"form": form})


@staff_member_required(login_url="admin:login")
def listing_delete_list(request):
    listings = Listing.objects.filter(is_active=True).select_related("category")
    query = request.GET.get("q", "").strip()

    if query:
        listings = listings.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(city__icontains=query)
            | Q(category__name__icontains=query)
        )

    return render(
        request,
        "elonlar/ochirish.html",
        {
            "listings": listings.order_by("-created_at"),
            "query": query,
            "total_count": listings.count(),
        },
    )


@staff_member_required(login_url="admin:login")
def listing_delete(request, slug):
    listing = get_object_or_404(
        Listing.objects.select_related("category"),
        slug=slug,
        is_active=True,
    )

    if request.method == "POST":
        listing.is_active = False
        listing.save(update_fields=["is_active", "updated_at"])
        messages.success(request, f"{listing.title} e'loni o'chirildi.")
        return redirect("elonlar:delete_list")

    return render(request, "elonlar/ochirish_tasdiq.html", {"listing": listing})


def google_setup(request):
    if not google_setup_allowed(request):
        messages.warning(request, "Google sozlash sahifasi faqat lokal kompyuterda ishlaydi.")
        return redirect("account_login")

    if request.method == "POST":
        form = GoogleSetupForm(request.POST)
        if form.is_valid():
            save_google_oauth(
                form.cleaned_data["client_id"].strip(),
                form.cleaned_data["client_secret"].strip(),
            )
            make_google_admin(
                form.cleaned_data["admin_email"],
                form.cleaned_data["admin_username"],
            )
            messages.success(request, "Google login sozlandi. Endi Google bilan kirishingiz mumkin.")
            return redirect("account_login")
    else:
        form = GoogleSetupForm()

    redirect_uri = request.build_absolute_uri("/accounts/google/login/callback/")
    return render(
        request,
        "elonlar/google_setup.html",
        {
            "form": form,
            "redirect_uri": redirect_uri,
            "is_debug": settings.DEBUG,
        },
    )


@login_required
def admin_password_reset(request):
    has_google_account = SocialAccount.objects.filter(user=request.user, provider="google").exists()

    if not request.user.is_staff:
        messages.warning(request, "Admin parolini o'zgartirish uchun staff/admin huquqi kerak.")
        return redirect("elonlar:home")

    if not has_google_account:
        messages.warning(request, "Bu sahifa faqat Google orqali ulangan admin uchun.")
        return redirect("elonlar:home")

    if request.method == "POST":
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Admin panel paroli yangilandi.")
            return redirect("admin:index")
    else:
        form = SetPasswordForm(request.user)

    return render(request, "elonlar/admin_password.html", {"form": form})


def admin_password_reset_request(request):
    if request.method == "POST":
        form = AdminPasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = _get_admin_by_email(email)

            if user:
                code = f"{secrets.randbelow(1000000):06d}"
                expires_at = timezone.now() + timedelta(minutes=ADMIN_RESET_TTL_MINUTES)
                request.session[ADMIN_RESET_SESSION_KEY] = {
                    "user_id": user.pk,
                    "code_hash": _admin_reset_code_hash(code),
                    "expires_at": expires_at.isoformat(),
                }
                request.session.modified = True
                send_mail(
                    subject="Elon admin parolni tiklash kodi",
                    message=(
                        f"Elon admin panel parolini tiklash kodi: {code}\n\n"
                        f"Kod {ADMIN_RESET_TTL_MINUTES} daqiqa amal qiladi."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

            messages.success(
                request,
                "Agar bu Gmail admin akkauntga ulangan bo'lsa, tiklash kodi yuborildi.",
            )
            return redirect("elonlar:admin_password_code")
    else:
        form = AdminPasswordResetRequestForm()

    return render(request, "elonlar/admin_password_request.html", {"form": form})


def admin_password_reset_code(request):
    reset_data = request.session.get(ADMIN_RESET_SESSION_KEY)
    User = get_user_model()
    user = None

    if reset_data:
        user = User.objects.filter(pk=reset_data.get("user_id"), is_staff=True, is_active=True).first()

    if not reset_data or not user:
        messages.warning(request, "Avval admin Gmailingizga kod yuboring.")
        return redirect("elonlar:admin_password_request")

    expires_at = timezone.datetime.fromisoformat(reset_data["expires_at"])
    if timezone.is_naive(expires_at):
        expires_at = timezone.make_aware(expires_at, timezone.get_current_timezone())

    if timezone.now() > expires_at:
        request.session.pop(ADMIN_RESET_SESSION_KEY, None)
        messages.warning(request, "Kod muddati tugagan. Yangi kod oling.")
        return redirect("elonlar:admin_password_request")

    if request.method == "POST":
        form = AdminPasswordCodeForm(user, request.POST)
        if form.is_valid():
            code_hash = _admin_reset_code_hash(form.cleaned_data["code"])
            if not secrets.compare_digest(code_hash, reset_data["code_hash"]):
                form.add_error("code", "Kod noto'g'ri.")
            else:
                form.save()
                request.session.pop(ADMIN_RESET_SESSION_KEY, None)
                messages.success(request, "Admin panel paroli yangilandi. Endi yangi parol bilan kiring.")
                return redirect("admin:login")
    else:
        form = AdminPasswordCodeForm(user)

    return render(request, "elonlar/admin_password_code.html", {"form": form})


def _verify_telegram_auth(data):
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise ValueError("Telegram bot token not configured")

    auth_data = dict(data)
    hash_received = auth_data.pop("hash", None)
    if not hash_received:
        raise ValueError("Missing hash")

    data_check_arr = [f"{k}={auth_data[k]}" for k in sorted(auth_data.keys())]
    data_check_string = "\n".join(data_check_arr)

    secret_key = hashlib.sha256(token.encode()).digest()
    hmac_digest = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(hmac_digest, hash_received):
        raise ValueError("Invalid telegram auth hash")

    auth_date = int(auth_data.get("auth_date", 0))
    if time.time() - auth_date > 86400:
        raise ValueError("Telegram auth expired")

    return auth_data


def telegram_login(request):
    # Telegram widget redirects with GET params
    try:
        auth = _verify_telegram_auth(request.GET)
    except Exception:
        messages.warning(request, "Telegram autentifikatsiya tasdiqlanmadi.")
        return redirect("account_login")

    User = get_user_model()
    tg_id = auth.get("id") or auth.get("user_id")
    username = f"tg_{tg_id}"

    user = User.objects.filter(username=username).first()
    if not user:
        user = User(username=username)
        user.set_unusable_password()
        user.first_name = auth.get("first_name", "")
        user.last_name = auth.get("last_name", "")
        email = auth.get("email")
        if email:
            user.email = email
        user.is_active = True
        user.save()

    auth_login(request, user)
    messages.success(request, "Telegram orqali tizimga kirdingiz.")
    return redirect(settings.LOGIN_REDIRECT_URL)

# Create your views here.
