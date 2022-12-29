from django.shortcuts import render
from ecommerce.apps.catalogue.models import Product
from django.db.models import Q
import logging

logger = logging.getLogger("console")

def search(request):
    products = Product.objects.all()
    logger.debug(f"{products.count()} productsz in total")
    logger.debug(f"request.GET is: {request.GET}")
    query = request.GET.get("q")
    logger.debug(f"received query: {query}")
    if query:
        lookup = Q(title__icontains=query) | Q(description__icontains=query)
        products=products.filter(lookup).distinct()
    logger.debug(f"{products.count()} products matched the query")
    return render(request, "search/search.html", {"products": products})
