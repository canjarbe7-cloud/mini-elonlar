from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField("Nomi", max_length=80, unique=True)
    slug = models.SlugField("Slug", max_length=90, unique=True, blank=True, allow_unicode=True)
    description = models.CharField("Qisqa izoh", max_length=160, blank=True)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True) or "kategoriya"
        super().save(*args, **kwargs)


class Listing(models.Model):
    class Condition(models.TextChoices):
        NEW = "new", "Yangi"
        USED = "used", "Ishlatilgan"

    CITY_CHOICES = [
        ("Toshkent", "Toshkent"),
        ("Samarqand", "Samarqand"),
        ("Buxoro", "Buxoro"),
        ("Andijon", "Andijon"),
        ("Namangan", "Namangan"),
        ("Farg'ona", "Farg'ona"),
        ("Qarshi", "Qarshi"),
        ("Nukus", "Nukus"),
    ]

    category = models.ForeignKey(
        Category,
        verbose_name="Kategoriya",
        on_delete=models.PROTECT,
        related_name="listings",
    )
    title = models.CharField("Sarlavha", max_length=140)
    slug = models.SlugField("Slug", max_length=160, unique=True, blank=True, allow_unicode=True)
    description = models.TextField("Tavsif")
    price = models.DecimalField("Narx", max_digits=12, decimal_places=0)
    city = models.CharField("Shahar", max_length=40, choices=CITY_CHOICES)
    address = models.CharField("Manzil", max_length=180, blank=True)
    seller_name = models.CharField("Sotuvchi", max_length=80)
    phone = models.CharField("Telefon", max_length=30)
    condition = models.CharField("Holati", max_length=12, choices=Condition.choices, default=Condition.USED)
    image = models.ImageField("Rasm", upload_to="elonlar/", blank=True)
    image_url = models.URLField("Tashqi rasm URL", blank=True)
    is_active = models.BooleanField("Faol", default=True)
    views = models.PositiveIntegerField("Ko'rishlar", default=0)
    created_at = models.DateTimeField("Qo'shilgan vaqt", auto_now_add=True)
    updated_at = models.DateTimeField("Yangilangan vaqt", auto_now=True)

    class Meta:
        verbose_name = "E'lon"
        verbose_name_plural = "E'lonlar"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("elonlar:detail", kwargs={"slug": self.slug})

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)[:110] or "elon"
            candidate = base_slug
            counter = 2
            while Listing.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = candidate
        super().save(*args, **kwargs)

# Create your models here.
