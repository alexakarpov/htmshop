from django.http import JsonResponse
from ecommerce.apps.accounts.models import Address
from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.shipping.choice import split_tiers
from ecommerce.apps.shipping.engine import shipping_choices
from rest_framework.decorators import api_view

from .serializers import ShippingChoiceSerializer


@api_view(http_method_names=["GET"])
def get_rates(request):
    basket = Basket(request)
    session = request.session
    address_id = session["address"]["address_id"]
    address = Address.objects.get(id=address_id)
    tiers = split_tiers(shipping_choices(basket, address))

    e = sorted(tiers["express"])[0]
    r = sorted(tiers["regular"])[0]
    f = sorted(tiers["fast"])[0]
    e.name = "Expedited"
    f.name = "Fast"
    r.name = "Economy"
    serializer = ShippingChoiceSerializer([r, f, e], many=True)
    sdata = serializer.data
    return JsonResponse({"choices": sdata})
