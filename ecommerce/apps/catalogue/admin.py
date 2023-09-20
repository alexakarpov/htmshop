from typing import Any, List, Tuple
from django import forms
from django.contrib import admin
import string

from .models import (
    Category,
    Product,
)

from mptt.admin import MPTTModelAdmin

admin.site.register(Category, MPTTModelAdmin)

# class ProductListFilter(admin.SimpleListFilter):
#     title = "Product Title Begins With Letter"
#     parameter_name = "startswith"

#     def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
#         return  [(x, x.upper()) for x in string.ascii_lowercase]

#     def queryset(self, request, queryset):
#         """
#         Returns the filtered queryset based on the value
#         provided in the query string and retrievable via
#         `self.value()`.
#         """
#         # Compare the requested value (either '80s' or '90s')
#         # to decide how to filter the queryset.
#         print(f"building a queryset with {self.value()}")
#         if self.value():
#             return queryset.filter(
#                 title__startswith=self.value()
#         )
#         else:
#             return queryset


class ProductAdmin(admin.ModelAdmin):
    ordering = ("title",)
    search_fields = ("title", "sku_base")
    list_filter = ("category",)


admin.site.register(Product, ProductAdmin)
