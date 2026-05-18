from django.contrib import admin

from .models import Category, Listing


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "city", "price", "seller_name", "is_active", "created_at")
    list_filter = ("is_active", "category", "city", "condition", "created_at")
    search_fields = ("title", "description", "seller_name", "phone", "city")
    list_editable = ("is_active",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("views", "created_at", "updated_at")

# Register your models here.
