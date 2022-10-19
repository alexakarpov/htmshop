import logging

from django.shortcuts import get_object_or_404, render

from .models import Category, Product

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
    # FIXME: this is now DB-driven
    # given a Product, get  all its ProductInventory items
    # ................ list all type's specs

    inventory = product.productinventory_set.all()
    variants = product.product_type.productspecification_set.all()

    logger.debug(
        f"product: {product}, type: {product.product_type}, variants: {inventory},")
    return render(request, "catalogue/single.html", {"product": product, "variants": variants})
