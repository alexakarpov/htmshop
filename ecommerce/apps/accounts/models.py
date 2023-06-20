import json
import logging
import uuid

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import gettext_lazy as _
from pytz import country_names

logger = logging.getLogger("django")


class CustomAccountManager(BaseUserManager):
    def validateEmail(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("You must provide a valid email address"))

    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True")

        if email:
            email = self.normalize_email(email)
            self.validateEmail(email)
        else:
            raise ValueError(_("Superuser Account: You must provide an email address"))

        return self.create_user(email, password, **other_fields)

    def create_user(self, email, password, **other_fields):
        if email:
            email = self.normalize_email(email)
            self.validateEmail(email)
        else:
            raise ValueError(_("Customer Account: You must provide an email address"))

        email = self.normalize_email(email)
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=20, blank=False, null=False)
    last_name = models.CharField(_("last name"), max_length=20, blank=False, null=False)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        # app_label = "accounts"
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def email_user(self, subject, message):
        logger.debug(f"emailing '{subject}' to {self.email}")
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_short_name(self):
        # otherwise there are strange error in the logs
        return self.get_first_name()

    def __str__(self):
        return self.email


class Address(models.Model):
    """
    Address
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Account, verbose_name=_("Account"), on_delete=models.CASCADE)
    full_name = models.CharField(_("Full Name"), max_length=25)
    phone = models.CharField(_("Phone Number"), max_length=20)
    postcode = models.CharField(_("Postal Code"), max_length=10)
    address_line = models.CharField(_("Address Line 1"), max_length=50)
    address_line2 = models.CharField(_("Address Line 2"), max_length=50, blank=True)
    town_city = models.CharField(_("Town/City"), max_length=50)
    state_province = models.CharField(_("State/Province"), max_length=10, blank=True)
    country = models.CharField(
        _("Country"), max_length=2, default="US", choices=country_names.items()
    )
    delivery_instructions = models.CharField(
        _("Delivery Instructions"), max_length=255, blank=True
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    default = models.BooleanField(_("Default"), default=False)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.full_name} address ({self.id}):\n{self.toJSON()}\n >>>>>>>>>"

    def from_dict(a_dict):
        a = Address()
        a.full_name = a_dict.get("full_name")
        a.address_line = a_dict.get("address_line1")
        a.address_line2 = a_dict.get("address_line2")
        a.phone = a_dict.get("phone")
        a.town_city = a_dict.get("city_locality")
        a.state_province = a_dict.get("state_province")
        a.postcode = a_dict.get("postal_code")
        a.country = a_dict.get("country_code")
        return a

    def to_dict(self):
        return {
            "full_name": self.full_name,
            "address_line1": self.address_line,
            "address_line2": self.address_line2,
            "phone": self.phone,
            "city_locality": self.town_city,
            "state_province": self.state_province,
            "postal_code": self.postcode,
            "country_code": self.country,
            # "address_residential_indicator": "yes", # used by SE
        }

    def toJSON(self):
        return json.dumps(self.to_dict(), indent=2)
