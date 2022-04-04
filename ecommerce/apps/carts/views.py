from django.shortcuts import redirect, render
from ecommerce.apps.carts.models import Cart
from ecommerce.apps.catalogue.models import Product


def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    return render(request, "carts/home.html", {"cart": cart_obj})
