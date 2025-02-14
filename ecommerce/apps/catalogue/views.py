import logging

from django.shortcuts import get_object_or_404, render, redirect

from ecommerce.constants import PHANURIUS_BOOK_SLUG
from ecommerce.constants import ID_LOOKUP

from .models import Category, Product

logger = logging.getLogger(__name__)

def catalogue_index(request):
    featured = Product.objects.filter(is_active=True, is_featured=True)
    return render(
        request,
        "catalogue/index.html",
        {"products": featured, "categories": Category.objects.all()},
    )


def legacy_product(request, legacy_id, ignored=None):
    sku = ID_LOOKUP.get(legacy_id)
    try:
        product = Product.objects.get(sku_base=sku)
        return redirect(product)
    except Product.DoesNotExist:
        return redirect("catalogue:home")


def category_list(request, category_slug=None, letter=None):
    cat = get_object_or_404(Category, slug=category_slug)

    products = cat.product_set.all().order_by("title")

    return render(
        request,
        "catalogue/category.html",
        {
            "category": cat,
            "products": products,
        },
    )


def saints_filtered(request, letter=None):
    saints = Category.objects.get(slug="icons-saints")
    saints_filtered = saints.product_set.filter(title__istartswith=letter)

    return render(
        request,
        "catalogue/category.html",
        {
            "category": saints,
            "products": saints_filtered,
        },
    )


def product_detail(request, slug):
    referrer = request.META.get("HTTP_REFERER")

    product = get_object_or_404(Product, slug=slug, is_active=True)

    # for books, filter out all OOS skus.
    if product.sku_base.startswith('B-'):
        skus = product.get_skus().filter(wrapping_qty__gt=0)
    else:
        skus = product.get_skus()
#    logger.warning(f"fetched {len(skus)} skus:")

#    for s in skus:
#        logger.warning(s)
    return render(
        request,
        "catalogue/single.html",
        {
            "product": product,
            "skus": skus,
            "referred": referrer,
        },
    )


def st_phanurius_book(request):
    # referrer = request.META.get("HTTP_REFERER")
    product = get_object_or_404(
        Product, slug=PHANURIUS_BOOK_SLUG, is_active=True
    )
    return redirect(product)
