from django.core.management.base import BaseCommand

from elonlar.models import Category, Listing


class Command(BaseCommand):
    help = "Demo kategoriya va e'lonlarni qo'shadi."

    def handle(self, *args, **options):
        categories = {
            "Elektronika": "Telefon, noutbuk va gadjetlar",
            "Uy-joy": "Ijara va sotuvdagi uylar",
            "Transport": "Avtomobil va ehtiyot qismlar",
            "Mebel": "Uy va ofis uchun mebellar",
            "Mol": "Qoramol e'lonlari",
            "Qo'y": "Qo'y va qo'chqor e'lonlari",
            "Ish": "Vakansiya va xizmatlar",
        }

        created_categories = {}
        for name, description in categories.items():
            category, _ = Category.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )
            created_categories[name] = category

        listings = [
            {
                "category": "Elektronika",
                "title": "iPhone 13 Pro 128GB",
                "description": "Yaxshi saqlangan, Face ID va batareyasi joyida. Korobka va zaryad kabeli bor.",
                "price": 6300000,
                "city": "Toshkent",
                "address": "Chilonzor",
                "seller_name": "Aziz",
                "phone": "+998 90 123 45 67",
                "condition": Listing.Condition.USED,
                "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?auto=format&fit=crop&w=900&q=80",
            },
            {
                "category": "Mebel",
                "title": "Yumshoq divan",
                "description": "Mehmonxona uchun qulay divan. Matosi toza, o'lchami 220x90 sm.",
                "price": 2800000,
                "city": "Samarqand",
                "address": "Registon yaqinida",
                "seller_name": "Madina",
                "phone": "+998 91 555 20 20",
                "condition": Listing.Condition.USED,
                "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=900&q=80",
            },
            {
                "category": "Transport",
                "title": "Spark 2022 avtomat",
                "description": "Yurgani 38 ming km. Kraska toza, konditsioner ishlaydi, hujjatlari tayyor.",
                "price": 98000000,
                "city": "Buxoro",
                "address": "Markaz",
                "seller_name": "Jasur",
                "phone": "+998 93 777 11 22",
                "condition": Listing.Condition.USED,
                "image_url": "https://images.unsplash.com/photo-1549924231-f129b911e442?auto=format&fit=crop&w=900&q=80",
            },
            {
                "category": "Uy-joy",
                "title": "2 xonali kvartira ijaraga",
                "description": "Shinam, remontli kvartira. Metroga yaqin, oilaga beriladi.",
                "price": 4200000,
                "city": "Toshkent",
                "address": "Yunusobod",
                "seller_name": "Dilshod",
                "phone": "+998 99 808 08 08",
                "condition": Listing.Condition.USED,
                "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80",
            },
            {
                "category": "Ish",
                "title": "Django junior dasturchi kerak",
                "description": "Ofisda ishlash, HTML/CSS va Django asoslarini bilish talab qilinadi.",
                "price": 5000000,
                "city": "Toshkent",
                "address": "Mirzo Ulugbek",
                "seller_name": "HR Manager",
                "phone": "+998 97 300 10 10",
                "condition": Listing.Condition.NEW,
                "image_url": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=900&q=80",
            },
        ]

        for item in listings:
            category_name = item.pop("category")
            Listing.objects.get_or_create(
                title=item["title"],
                defaults={"category": created_categories[category_name], **item},
            )

        self.stdout.write(self.style.SUCCESS("Demo ma'lumotlar tayyor."))
