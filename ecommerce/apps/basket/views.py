import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from ecommerce.apps.catalogue.models import Product

from .basket import Basket

logger = logging.getLogger("console")

def basket_summary(request):
    user = request.user
    basket = Basket(request)
    logger.debug("in basket/views/basket_summary")

    return render(request, "basket/summary.html", {"basket": basket, "user": user})


def basket_add(request):
    basket = Basket(request)
    logger.debug(f"POST: {request.POST}")
    if request.POST.get("action") == "post":
        product_id = int(request.POST.get("productid"))
        product_qty = int(request.POST.get("productqty"))
        variant = str(request.POST.get("variant"))
        product = get_object_or_404(Product, id=product_id)
        basket.add(product=product, qty=product_qty, variant=variant)
        basketqty = basket.__len__()
        response = JsonResponse({"qty": basketqty})
        return response


def basket_delete(request):
    basket = Basket(request)

    if request.POST.get("action") == "post":
        product_id = int(request.POST.get("productid"))
        basket.delete(product_id=product_id)
        basketqty = basket.__len__()
        baskettotal = basket.get_total()
        response = JsonResponse({"qty": basketqty, "subtotal": baskettotal})
        return response


def basket_update(request):
    logger.debug(f"POST: {request.POST}")

    basket = Basket(request)

    if request.POST.get("action") == "post":
        product_id = int(request.POST.get("productid"))
        product_qty = int(request.POST.get("productqty"))
        basket.update(product_id=product_id, qty=product_qty)

        basketqty = basket.__len__()
        basketsubtotal = basket.get_subtotal_price()
        return JsonResponse({"qty": basketqty, "subtotal": basketsubtotal})
