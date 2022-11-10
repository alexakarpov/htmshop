import logging
from distutils.log import debug

from django.http import JsonResponse
from django.shortcuts import get_list_or_404, render

from ecommerce.apps.catalogue.models import Product, ProductInventory

from .basket import Basket

logger = logging.getLogger("console")


def basket_summary(request):
    user = request.user
    basket = Basket(request)
    logger.debug(f"summary of basket {basket}")
    for sku, item in basket.basket.items():
        logger.debug(f"summary > {sku}: {item}")

    return render(
        request, "basket/summary.html", {"basket": basket, "user": user}
    )


def basket_add(request):
    basket = Basket(request)
    logger.debug(f"basket_add POST: {request.POST}")
    if request.POST.get("action") == "post":
        product_qty = int(request.POST.get("productqty"))
        variant = request.POST.get("variant")  # may be None
        product_id = request.POST.get("productid")

        if variant:
            # we can fetch PRI by the supplied SKU
            logger.debug(f"to add variant/sku: {variant}")
            pri = ProductInventory.objects.get(sku=variant)
            logger.debug(f"item: {pri}")
            basket.add(product=pri, qty=product_qty, sku=variant)
        else:
            # we can fetch the unique PRI by using the product itself
            logger.debug(f"adding a product without variants")
            pri = ProductInventory.objects.get(product=product_id)
            basket.add(product=pri, qty=product_qty, sku=pri.sku)

        basketqty = basket.__len__()
        return JsonResponse({"qty": basketqty})


def basket_delete(request):
    basket = Basket(request)
    logger.debug(f"basket_delete POST: {request.POST}")
    if request.POST.get("action") == "post":
        # well yeah: basket_delete POST: <QueryDict: {'productid': ['']
        sku_in = request.POST.get("sku")
        logger.debug(
            f"requested to remove {sku_in} from the cart in {basket} ({type(basket)}"
        )
        logger.debug(f"basket before: {basket}")
        basket.delete(sku=sku_in)
        logger.debug(f"basket after: {basket}")
        basketqty = basket.__len__()
        baskettotal = basket.get_total()
        response = JsonResponse({"qty": basketqty, "subtotal": baskettotal})
        return response


def basket_update(request):
    logger.debug(f"POST: {request.POST}")

    basket = Basket(request)

    if request.POST.get("action") == "post":
        sku = request.POST.get("sku")
        logger.debug(f"Cart Item for update: {sku}")
        assert sku != ""
        sku_qty = int(request.POST.get("skuqty"))
        basket.update(sku=sku, qty=sku_qty)

        basketqty = basket.__len__()
        basketsubtotal = basket.get_subtotal_price()
        return JsonResponse({"qty": basketqty, "subtotal": basketsubtotal})
