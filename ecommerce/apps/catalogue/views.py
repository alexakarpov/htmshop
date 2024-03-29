import logging

from django.shortcuts import get_object_or_404, render, redirect

from ecommerce.constants import PHANURIUS_BOOK_SLUG
from ecommerce.constants import idlookup

from .models import Category, Product

logger = logging.getLogger("django")


def catalogue_index(request):
    featured = Product.objects.filter(is_active=True, is_featured=True)
    return render(
        request,
        "catalogue/index.html",
        {"products": featured, "categories": Category.objects.all()},
    )


def legacy_product(request, legacy_id, ignored=None):
    sku = idlookup.get(legacy_id)
    try:
        product = Product.objects.get(sku_base=sku)
        return redirect(product)
    except Product.DoesNotExist:
        return redirect("catalogue:home")

def catalogue_new(request):
    products = Product.objects.filter(is_active=True)
    logger.debug("catalogue new")
    return render(
        request,
        "catalogue/wip_index.html",
        {"products": products, "categories": Category.objects.all()},
    )


def category_list(request, category_slug=None, letter=None):
    print(f"getting cat by slug {category_slug}")
    cat = get_object_or_404(Category, slug=category_slug)

    products = cat.product_set.all().order_by("title")

    # for c in category.get_descendants():
    #     products += list(c.product_set.all())

    print(f"got {len(products)} products for {category_slug}")

    return render(
        request,
        "catalogue/category.html",
        {
            "category": cat,
            "products": products,
            "categories": Category.objects.all(),
        },
    )


def saints_filtered(request, letter=None):
    saints = Category.objects.get(slug="icons-saints")
    saints_filtered = saints.product_set.filter(title__startswith=letter)

    return render(
        request,
        "catalogue/category.html",
        {
            "category": saints,
            "products": saints_filtered,
            "categories": Category.objects.all(),
        },
    )


def product_detail(request, slug):
    referrer = request.META.get("HTTP_REFERER")

    product = get_object_or_404(Product, slug=slug, is_active=True)
    skus = product.get_skus()
    logger.debug(f"fetched {len(skus)} skus")
    return render(
        request,
        "catalogue/single.html",
        {
            "product": product,
            "skus": skus,
            "referred": referrer,
            "categories": Category.objects.all(),
        },
    )


def st_phanurius_book(request):
    referrer = request.META.get("HTTP_REFERER")
    product = get_object_or_404(
        Product, slug=PHANURIUS_BOOK_SLUG, is_active=True
    )
    return redirect(product)
