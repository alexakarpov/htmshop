from django.contrib import admin

from .models import (
    ProductStock,
    ProductSpecification,
    ProductSpecificationValue,
    ProductType,
    Stock,
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
class ProductInventoryAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationValueInline,
    ]

    def get_inlines(self, request, obj):
        if not obj or not obj.id or not obj.product_type:
            return []  # ... then don't show any inlines
        return self.inlines

class StockInline(admin.TabularInline):
    model = Stock

admin.site.register(Stock)
