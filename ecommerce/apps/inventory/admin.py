from django.contrib import admin

from .models import (
    Stock,
    ProductType,
)

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    pass



@admin.register(Stock)
class ProductStockAdmin(admin.ModelAdmin):
    ordering = ('sku',)

    def get_inlines(self, request, obj):
        if not obj or not obj.sku or not obj.product_type:
            return []  # ... then don't show any inlines
        return self.inlines
