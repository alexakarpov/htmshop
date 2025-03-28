import logging

from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator

from ecommerce.constants import PHANURIUS_BOOK_SLUG
from ecommerce.constants import ID_LOOKUP

from .models import Category, Product
from .utils import reorder

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
    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "catalogue/category.html",
        {
            "category": cat,
            "page_obj": page_obj,
            "products": paginator,
        },
    )


def saints_filtered(request, letter=None):
    saints = Category.objects.get(slug="icons-saints")
    saints_filtered = saints.product_set.filter(title__istartswith=letter)

    paginator = Paginator(saints_filtered, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "catalogue/category.html",
        {
            "category": saints,
            "page_obj": page_obj,
            "products": paginator,
        },
    )


def product_detail(request, slug):
    referrer = request.META.get("HTTP_REFERER")

    product = get_object_or_404(Product, slug=slug, is_active=True)

    # for books, filter out all OOS skus.
    if product.sku_base.startswith("B-"):
        skus = product.get_skus().filter(wrapping_qty__gt=0)
    else:
        skus = product.get_skus()

    if len(skus) == 1:
        return render(
            request,
            "catalogue/single.html",
            {
                "product": product,
                "skus": skus,
                "referred": referrer,
            },
        )
    elif product.sku_base.startswith('A-'):
        ss, ers, ps = reorder(skus)
        return render(
            request,
            "catalogue/icons.html",
            {
                "product": product,
                "skus": skus,
                "ss": ss,
                "ers": sorted(ers),
                "ps": sorted(ps),
                "referred": referrer,
            },
        )
    else:
        return render(
            request,
            "catalogue/choice.html",
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
