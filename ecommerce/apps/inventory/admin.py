from django.contrib import admin

from .models import (
    ProductStock,
    ProductSpecification,
    ProductSpecificationValue,
    ProductType,
)

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationInline,
    ]


class ProductSpecificationValueInline(admin.TabularInline):
    model = ProductSpecificationValue


@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationValueInline,
    ]

    def get_inlines(self, request, obj):
        if not obj or not obj.sku or not obj.product_type:
            return []  # ... then don't show any inlines
        return self.inlines
