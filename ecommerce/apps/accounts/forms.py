import logging

from attr import attrs
from django import forms
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserChangeForm,
    UserCreationForm,
)
from django.utils.translation import gettext_lazy as _

from .models import Address

# from django_countries.fields import CountryField


UserModel = get_user_model()

logger = logging.getLogger("django")


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "full_name",
            "phone",
            "address_line",
            "address_line2",
            "town_city",
            "state_province",
            "postcode",
            "country",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].widget.attrs.update(
            {"class": "form-control mb-2 account-form",
                "placeholder": _("Full Name")}
        )
        self.fields["phone"].widget.attrs.update(
            {"class": "form-control mb-2 account-form", "placeholder": "Phone"})
        self.fields["address_line"].widget.attrs.update(
            {"class": "form-control mb-2 account-form",
                "placeholder": _("Address Line 1")}
        )
        self.fields["address_line2"].widget.attrs.update(
            {"class": "form-control mb-2 account-form",
                "placeholder": _("Address Line 2")}
        )
        self.fields["town_city"].widget.attrs.update(
            {"class": "form-control mb-2 account-form",
                "placeholder": _("Town/City")}
        )
        self.fields["state_province"].widget.attrs.update(
            {"class": "form-control mb-2 account-form",
                "placeholder": _("State/Province")}
        )
        self.fields["postcode"].widget.attrs.update(
            {"class": "form-control mb-2 account-form",
                "placeholder": _("Postal code")}
        )
        self.fields["country"].widget.attrs.update(
            {"class": "form-control mb-2 account-form"})

        self.fields["address_line2"].required = False


class EmailAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={"class": "form-control mb-3", "placeholder": "Email", "id": "login-email"})
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": _(f"Please enter a correct email and password."),
        "inactive": _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        self.email_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        if email is not None and password:
            self.user_cache = authenticate(
                self.request, email=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return forms.ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
            params={"email": self.email_field.verbose_name},
        )


class AccountCreationForm(UserCreationForm):
    """Require email address when a user signs up"""

    email = forms.EmailField(label="Email address", max_length=75)

    class Meta:
        model = UserModel
        fields = (
            # "username",
            "email",
        )

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            user = UserModel.objects.get(email=email)
            raise forms.ValidationError(
                "This email address already exists. Did you forget your password?")
        except UserModel.DoesNotExist:
            return email

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email"]
        user.is_active = True  # change to false if using email activation
        if commit:
            user.save()
            return user


class AccountChangeForm(UserChangeForm):
    class Meta:
        model = UserModel
        fields = ("email", "password")


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        max_length=100,
        help_text="Required",
        error_messages={"required": "Sorry, you will need an email"},
    )
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Repeat password", widget=forms.PasswordInput)
    name = forms.CharField(
        label="Short name", required=False, widget=forms.TextInput())

    class Meta:
        model = UserModel
        fields = ("email",)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get("password") != cd.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cd["password2"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if UserModel.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Please use another Email, that is already taken")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {"class": "form-control mb-3", "placeholder": "E-mail",
                "name": "email", "id": "id_email"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control mb-3", "placeholder": "Password"})
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control mb-3", "placeholder": "Repeat Password"})
        self.fields["name"].widget.attrs.update(
            {"class": "form-control",
                "placeholder": "opional short name on account", "id": "short-name"}
        )


class PwdResetForm(PasswordResetForm):

    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(
            attrs={"class": "form-control mb-3", "placeholder": "Email", "id": "form-email"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        u = UserModel.objects.filter(email=email)
        if not u:
            raise forms.ValidationError(
                "Unfortunatley we can not find that email address")
        return email


class PwdResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control mb-3",
                   "placeholder": "New Password", "id": "form-newpass"}
        ),
    )
    new_password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control mb-3",
                   "placeholder": "New Password", "id": "form-new-pass2"}
        ),
    )


class UserEditForm(forms.ModelForm):

    email = forms.EmailField(
        label="Account email (can not be changed)",
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control mb-3", "placeholder": "email",
                   "id": "form-email", "readonly": "readonly"}
        ),
    )

    name = forms.CharField(
        label="Your name or nickname",
        max_length=30,
        widget=forms.TextInput(
            attrs={"class": "form-control mb-3",
                   "placeholder": "short name", "id": "form-short-name"}
        ),
    )

    class Meta:
        model = UserModel
        fields = ("email", "name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
