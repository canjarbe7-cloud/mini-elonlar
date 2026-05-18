from django import forms
from django.contrib.auth.forms import SetPasswordForm

from .auth_helpers import GOOGLE_CLIENT_ID_SUFFIX, looks_like_google_client_id
from .models import Listing


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            "category",
            "title",
            "description",
            "price",
            "city",
            "address",
            "seller_name",
            "phone",
            "condition",
            "image",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Masalan: iPhone 13 Pro 128GB"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Mahsulot haqida qisqacha yozing"}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "1000", "placeholder": "Narx so'mda"}),
            "address": forms.TextInput(attrs={"placeholder": "Masalan: Chilonzor tumani"}),
            "seller_name": forms.TextInput(attrs={"placeholder": "Ismingiz"}),
            "phone": forms.TextInput(attrs={"placeholder": "+998 90 123 45 67"}),
        }


class GoogleSetupForm(forms.Form):
    client_id = forms.CharField(
        label="Google Client ID",
        widget=forms.TextInput(attrs={"placeholder": "Google Cloud'dagi Client ID"}),
    )
    client_secret = forms.CharField(
        label="Google Client Secret",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Google Cloud'dagi Client Secret"},
            render_value=True,
        ),
    )
    admin_email = forms.EmailField(
        label="Admin Gmail",
        widget=forms.EmailInput(attrs={"placeholder": "sizning@gmail.com"}),
    )
    admin_username = forms.CharField(
        label="Admin username",
        initial="admin",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "admin"}),
    )

    def clean_client_id(self):
        client_id = self.cleaned_data["client_id"].strip()
        if not looks_like_google_client_id(client_id):
            raise forms.ValidationError(
                f"Google Client ID {GOOGLE_CLIENT_ID_SUFFIX} bilan tugashi kerak."
            )
        return client_id

    def clean_client_secret(self):
        return self.cleaned_data["client_secret"].strip()


class AdminPasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Admin Gmail",
        widget=forms.EmailInput(attrs={"placeholder": "admin@gmail.com"}),
    )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


class AdminPasswordCodeForm(SetPasswordForm):
    code = forms.CharField(
        label="Emaildagi kod",
        min_length=6,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "placeholder": "123456",
                "autocomplete": "one-time-code",
                "inputmode": "numeric",
            }
        ),
    )

    field_order = ["code", "new_password1", "new_password2"]

    def clean_code(self):
        code = self.cleaned_data["code"].strip()
        if not code.isdigit():
            raise forms.ValidationError("Kod faqat raqamlardan iborat bo'lishi kerak.")
        return code
