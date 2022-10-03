from django import forms
from django.contrib import admin

from .models import (Category, Product, ProductImage, ProductSpecification,
                     ProductSpecificationValue, ProductType)

admin.site.register(Category)


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification


@ admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationInline,
    ]


class ProductSpecificationValueInline(admin.TabularInline):
    model = ProductSpecificationValue


class ProductImageInline(admin.TabularInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductImageInline,
        ProductSpecificationValueInline,
    ]
