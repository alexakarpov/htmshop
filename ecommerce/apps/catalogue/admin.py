from django import forms
from django.contrib import admin

from .models import (
    Category,
    Product,
    ProductImage,
    ProductInventory,
    ProductSpecification,
    ProductSpecificationValue,
    ProductType,
)

admin.site.register(Category)
admin.site.register(Product)


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationInline,
    ]


class ProductSpecificationValueInline(admin.TabularInline):
    model = ProductSpecificationValue


@admin.register(ProductInventory)
class ProductInventoryAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationValueInline,
    ]

    def get_inlines(self, request, obj):
        if not obj or not obj.id or not obj.product.product_type:
            return []  # ... then don't show any inlines
        return self.inlines
