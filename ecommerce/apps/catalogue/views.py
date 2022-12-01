import logging

from django.shortcuts import get_object_or_404, render

from .models import Category, Product, ProductInventory

logger = logging.getLogger("console")


def catalogue_index(request):
    products = Product.objects.filter(is_active=True)
    return render(request, "catalogue/index.html", {"products": products})


def get_children_products(cat):
    all_products = Product.objects.all()
    relevant_products = []

    for p in all_products:
        if p.category in cat.children.all():
            relevant_products.append(p)

    return relevant_products


def category_list(request, category_slug=None):
    logger.debug(f"fetching products for category by slug - {category_slug}")
    category = get_object_or_404(Category, slug=category_slug)
    products = (
        Product.objects.filter(category__slug=category_slug)
        if category.children.count() == 0
        else get_children_products(category)
    )

    return render(
        request,
        "catalogue/category.html",
        {"category": category, "products": products},
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    variants = product.get_variants()
    label = None
    if variants.count() > 1:
        label = (
            variants[0]
            .productspecificationvalue_set.first()
            .specification.name
        )

    logger.debug(
        f"product: {product}, type: {product.product_type}, variants: {variants}, label:{label}"
    )
    return render(
        request,
        "catalogue/single.html",
        {"product": product, "variants": variants, "label": label},
    )
