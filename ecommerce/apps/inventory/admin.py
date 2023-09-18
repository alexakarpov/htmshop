from django.contrib import admin

from .models import (
    Stock,
)


@admin.register(Stock)
class ProductStockAdmin(admin.ModelAdmin):
    ordering = ("sku",)
    search_fields = ("sku", "product__title")
