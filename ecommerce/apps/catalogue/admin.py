from django import forms
from django.contrib import admin

from .models import (
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
    ProductType,
)

admin.site.register(Category)


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [
        ProductAttributeInline,
    ]


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductAttributeValueInline,
        ProductImageInline,
    ]
