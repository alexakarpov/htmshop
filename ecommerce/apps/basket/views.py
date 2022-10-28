import logging

from django.http import JsonResponse
from django.shortcuts import get_list_or_404, render

from ecommerce.apps.catalogue.models import Product, ProductInventory

from .basket import Basket

logger = logging.getLogger("console")

def basket_summary(request):
    user = request.user
    basket = Basket(request)
    logger.debug(f"in basket_summary for {basket}")

    return render(request, "basket/summary.html", {"basket": basket, "user": user})


def basket_add(request):
    basket = Basket(request)
    logger.debug(f"POST: {request.POST}")
    if request.POST.get("action") == "post":
        product_id = int(request.POST.get("productid"))
        logger.debug(f"POST had the key productid, with value of {product_id}")
        product_qty = int(request.POST.get("productqty"))
        logger.debug(f"POST keys: {request.POST.keys()}")
        variant = request.POST.get("variant")
        
        # need to add ProductInventory item, which has a price, not Product entity, which doesn't
        
        product_items = get_list_or_404(ProductInventory, product=product_id)
        logger.debug(f"got {len(product_items)} of SKUs/Inventory Items for Product# {product_id}")
        
        # What if the Product had no variant? pri needs to have price, sku and weight
        for p in product_items:
            if variant and p.productspecificationvalue_set.reverse().first().value == variant:
                pri = p
            else:
                pri = product_items[0] # if there's no variant in the request, then the item is unique for this Product

        basket.add(product=pri,
                   qty=product_qty,
                   pid=product_id,
                   variant=variant)
        basketqty = basket.__len__()
        response = JsonResponse({"qty": basketqty})
        return response


def basket_delete(request):
    basket = Basket(request)
    logger.debug(f"basket_delete POST: {request.POST}")
    if request.POST.get("action") == "post":
        # well yeah: basket_delete POST: <QueryDict: {'productid': ['']
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
