import logging
from distutils.log import debug

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_list_or_404, render

from ecommerce.apps.inventory.models import ProductStock

from .basket import Basket

logger = logging.getLogger("django")


def basket_summary(request):
    user = request.user
    basket = Basket(request)

    # for sku, item in basket.basket.items():
    #     logger.debug(f"basket summary > {sku}: {item}")

    return render(request, "basket/summary.html", {"basket": basket, "user": user})


def basket_add(request):
    basket = Basket(request)
    next = request.POST.get("next", "/")

    if request.POST.get("action") == "post":
        product_qty = int(request.POST.get("productqty"))

        sku = request.POST.get("sku")

        inventoryitem = ProductStock.objects.get(sku=sku)

        basket.add(product=inventoryitem, qty=product_qty, sku=sku)

        basketqty = basket.__len__()
        return JsonResponse({"qty": basketqty, "next": next})


def basket_delete(request):
    basket = Basket(request)

    if request.POST.get("action") == "post":
        sku_in = request.POST.get("sku")
        basket.delete(sku=sku_in)
        basketqty = basket.__len__()
        baskettotal = basket.get_total()
        response = JsonResponse({"qty": basketqty, "subtotal": baskettotal})
        return response


def basket_update(request):
    logger.debug(f"POST: {request.POST}")

    basket = Basket(request)

    if request.POST.get("action") == "post":
        sku = request.POST.get("sku")
        assert sku != ""
        sku_qty = int(request.POST.get("skuqty"))
        basket.update(sku=sku, qty=sku_qty)

        basketqty = basket.__len__()
        basketsubtotal = basket.get_subtotal_price()
        return JsonResponse({"qty": basketqty, "subtotal": basketsubtotal})
