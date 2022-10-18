from django import forms
from django.contrib import admin

from .models import (Category, Product, ProductImage, ProductInventory,
                     ProductSpecification, ProductSpecificationValue,
                     ProductType)

admin.site.register(Category)


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification


admin.site.register(Product)


@ admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationInline,
    ]


class ProductSpecificationValueInline(admin.TabularInline):
    model = ProductSpecificationValue

    # def get_fieldsets(self, request, obj=None):
    #     print(f">>>>>>>>> PSVI.get_fieldsets begins")
    #     fisets = super().get_fieldsets(request, obj)
    #     print(f">>>>>>>>> PSVI.get_fieldsets ends")
    #     return fisets

    # def get_formset(self, request, obj1=None, **kwargs):  # obj is always the current Product
    #     print(f">>>>>>>>> PSVI.get_formset begins")
    #     print(f"obj1: {obj1}")

    #     fset = super().get_formset(request, obj1, **kwargs)

    #     print(f">>>>>>>>> PSVI.get_formset ends")
    #     return fset

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     print(f">>>> ffffk({db_field.name}) begins, kwargs: {kwargs}")

    #     if db_field.name == "specification":
    #         field = super(ProductSpecificationValueInline, self).formfield_for_foreignkey(
    #             db_field, request, **kwargs)

    #         parent_id = request.resolver_match.args[0]
    #         print(f"pid:{parent_id}")

    #         kwargs["queryset"] = ProductSpecification.objects.all()

    #         #filter('product_type' == super().obj.product_type)

    #         print(f"self: {self}, dir: {dir(self)}, model: {self.model}")
    #         # print(f"dir(request): {dir(request)}")
    #         qs = field.queryset
    #         # ok model here is ProductSpecification
    #         print(f"qs: {qs}\n dir(qs):\n{dir(qs)}\nmodel:{qs.model}")
    #         # qs = qs.filter(self.product_type == obj1.product_type)
    #     ffffk = super().formfield_for_foreignkey(db_field, request, **kwargs)
    #     print(f">>>> ffffk {db_field.name}  ends")
    #     return ffffk


@ admin.register(ProductInventory)
class ProductInventoryAdmin(admin.ModelAdmin):

    # def get_queryset(self, request):
    #     # print(f">>>>>>>>>>>>>>>>>>>>>> get_queryset of PIAdmin begins")
    #     # this queryset will only contain the PI object itself
    #     qs = super().get_queryset(request)
    #     # print(f"<<<<<<<<<<<<<<<<<<<<<< get_queryset of PIAdmin ends")
    #     return qs

    inlines = [
        ProductSpecificationValueInline,
    ]

    def get_inlines(self, request, obj):
        if not obj or not obj.id or not obj.product.product_type:
            return []  # ... then don't show any inlines
        return self.inlines
