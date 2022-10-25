import logging

from django.shortcuts import get_object_or_404, render

from .models import Category, Product, ProductInventory

logger = logging.getLogger("console")


def product_all(request):
    products = Product.objects.prefetch_related(
        "product_image").filter(is_active=True)
    return render(request, "catalogue/index.html", {"products": products})


def category_list(request, category_slug=None):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category__slug=category_slug)
    return render(request, "catalogue/category.html", {"category": category, "products": products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # @TODO: get the SKU out of Product+Variant, and pass it in place of the Product

    variants = product.get_variants()
    # if it's a single variant, template won't even show the drop-down
    if len(variants) == 1:
        sku = ProductInventory.objects.get(product_id=product.id)
        variants = []
    

    logger.debug(
        f"product: {product}, type: {product.product_type}, variants: {variants},")
    return render(request, "catalogue/single.html", {"product": product, "variants": variants})
