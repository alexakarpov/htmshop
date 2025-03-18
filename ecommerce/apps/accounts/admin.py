from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account, Address


class AccountAdmin(UserAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                    "first_name",
                    "last_name",
                    "last_login",
                    "debt",
                    "credit_limit"
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_trusted",
                    "is_staff",
                    "is_superuser",
                    "is_bookstore",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_bookstore",
        "last_login",
        "debt",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "is_trusted", "is_bookstore", "groups")
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

class AddressAdmin(admin.ModelAdmin):
    model = Address
    search_fields = ("full_name","address_line1", "address_line2", "postal_code", "phone", "city_locality")


admin.site.register(Account, AccountAdmin)
admin.site.register(Address, AddressAdmin)
