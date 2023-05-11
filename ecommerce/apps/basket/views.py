import logging
from distutils.log import debug

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_list_or_404, render

from ecommerce.apps.inventory.models import ProductStock


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
    if request.POST.get("action") == "post":
        product_qty = int(request.POST.get("productqty"))

        sku = request.POST.get("sku")

        inventoryitem = ProductStock.objects.get(sku=sku)
        logger.debug(f"item: {inventoryitem}")
        basket.add(product=inventoryitem, qty=product_qty, sku=sku)

        basketqty = basket.__len__()
        return JsonResponse({"qty": basketqty})

def add_to_cart(request):
    basket = Basket(request)
    product_qty = int(request.POST.get("productqty"))
    sku = request.POST.get("sku")
    next = request.POST.get('next', '/')
    next2 = request.META.get('HTTP_REFERER')
    logger.info(f"redirecting to: {next} or {next2}")
    inventoryitem = ProductStock.objects.get(sku=sku)
    
    # need to make sure the cart is updated and redirect is done to the proper url
    # for now this method/view isn't even invoked
    basket.add(product=inventoryitem, qty=product_qty, sku=sku)
    basketqty = basket.__len__()
    return HttpResponseRedirect(next2)

def basket_delete(request):
    basket = Basket(request)
    # logger.debug(f"basket_delete POST: {request.POST}")
    if request.POST.get("action") == "post":
        sku_in = request.POST.get("sku")
        logger.debug(
            f"requested to remove {sku_in} from the cart in {basket} ({type(basket)}"
        )
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
        logger.debug(f"Cart Item for update: {sku}")
        assert sku != ""
        sku_qty = int(request.POST.get("skuqty"))
        basket.update(sku=sku, qty=sku_qty)

        basketqty = basket.__len__()
        basketsubtotal = basket.get_subtotal_price()
        return JsonResponse({"qty": basketqty, "subtotal": basketsubtotal})
