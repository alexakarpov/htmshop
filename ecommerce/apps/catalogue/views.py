import logging

from django.shortcuts import get_object_or_404, render

from .models import Category, Product

logger = logging.getLogger("console")


def catalogue_index(request):
    products = Product.objects.filter(is_active=True)
    logger.debug(f"all products - {products.count()} are active")
    return render(request, "catalogue/index.html", {"products": products})


def catalogue_new(request):
    products = Product.objects.filter(is_active=True)
    logger.debug("catalogue new")
    return render(request, "catalogue/wip_index.html", {"products": products})


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
    skus = product.get_skus()
    logger.debug(f"fetched {len(skus)} skus")
    return render(
        request,
        "catalogue/single.html",
        {"product": product, "skus": skus },
    )
