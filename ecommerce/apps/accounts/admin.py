from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import AccountChangeForm, AccountCreationForm
from .models import Account


class AccountAdmin(UserAdmin):
    add_form = AccountCreationForm
    form = AccountChangeForm
    model = Account
    list_display = [
        "email",
        "name",
    ]
    ordering = [
        "email",
    ]


admin.site.register(Account, AccountAdmin)
