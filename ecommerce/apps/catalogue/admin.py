from django import forms
from django.contrib import admin

from .models import (
    Category,
    Product,
)

from mptt.admin import MPTTModelAdmin

admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Product)
