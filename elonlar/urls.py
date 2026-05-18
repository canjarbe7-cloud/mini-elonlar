from django.urls import path

from . import views

app_name = "elonlar"

urlpatterns = [
    path("", views.listing_list, name="home"),
    path("google-sozlash/", views.google_setup, name="google_setup"),
    path("telegram/login/", views.telegram_login, name="telegram_login"),
    path("admin-parol/", views.admin_password_reset, name="admin_password"),
    path("admin-parol/tiklash/", views.admin_password_reset_request, name="admin_password_request"),
    path("admin-parol/kod/", views.admin_password_reset_code, name="admin_password_code"),
    path("qoshish/", views.listing_create, name="create"),
    path("ochirish/", views.listing_delete_list, name="delete_list"),
    path("elon/<slug:slug>/ochirish/", views.listing_delete, name="delete"),
    path("elon/<slug:slug>/", views.listing_detail, name="detail"),
]
