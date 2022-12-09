from django.shortcuts import render
from ecommerce.apps.catalogue.models import Product
from django.db.models import Q
import logging

logger = logging.getLogger("console")


def search(request):
    products = Product.objects.all()
    query = request.GET.get("q")
    if query:
        lookup = Q(title__icontains=query) | Q(description__icontains=query)
        products=products.filter(lookup).distinct()

    return render(request, "search/index.html", {"products": products})
