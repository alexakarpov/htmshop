from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from ecommerce.apps.catalogue.models import Product
from ecommerce.apps.shipping.choice import ShippingChoice
from ecommerce.utils import variants

from .basket import Basket, get_weight


def basket_summary(request):
    user = request.user
    basket = Basket(request)
    w = get_weight(basket.basket.values())
    return render(request, "basket/summary.html", {"basket": basket, "user": user})


def basket_add(request):
    basket = Basket(request)
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
    basket = Basket(request)

    if request.POST.get("action") == "post":
        product_id = int(request.POST.get("productid"))
        product_qty = int(request.POST.get("productqty"))
        basket.update(product_id=product_id, qty=product_qty)

        basketqty = basket.__len__()
        basketsubtotal = basket.get_subtotal_price()
        return JsonResponse({"qty": basketqty, "subtotal": basketsubtotal})
