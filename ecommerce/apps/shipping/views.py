import json
import logging

from django.http import JsonResponse
from rest_framework.decorators import api_view

from ecommerce.apps.accounts.models import Address
from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.shipping.choice import split_tiers
from ecommerce.apps.shipping.engine import shipping_choices
from ecommerce.utils import debug_print

from .serializers import ShippingChoiceSerializer

logger = logging.getLogger("console")


@api_view(http_method_names=["GET"])
def get_rates(request):
    basket = Basket(request)
    session = request.session
    logger.debug(" in shipping.views/get_rates")

    address_json = session["address"]
    logger.debug(f"JSON from the session:\n{address_json}")
    d = json.loads(address_json)
    logger.debug(f"JSON dict loaded:\n{d}")
    address = Address.fromJSONDict(d)
    logger.debug(f"JSON dict loaded:\n{address}")
    choices = shipping_choices(basket, address)

    if len(choices) == 0:
        logger.warn("no rates in SE response?")
        return JsonResponse({"choices": []})

    logger.debug(f"CHOICES: {choices}")
    tiers = split_tiers(choices)
    logger.debug(f"TIERS: {tiers}")

    e = sorted(tiers["express"])[0]
    r = sorted(tiers["regular"])[0]
    f = sorted(tiers["fast"])[0]
    e.name = "Expedited"
    f.name = "Fast"
    r.name = "Economy"
    serializer = ShippingChoiceSerializer([r, f, e], many=True)
    sdata = serializer.data
    return JsonResponse({"choices": sdata})
