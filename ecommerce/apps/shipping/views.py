import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, renderer_classes
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from ecommerce.apps.accounts.models import Address
from ecommerce.apps.orders.models import Order
from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.shipping.choice import split_tiers
from ecommerce.apps.shipping.engine import shipping_choices

from .serializers import OrderSerializer, ShippingChoiceSerializer

logger = logging.getLogger("django")


class OrdersXMLRenderer(XMLRenderer):
    root_tag_name = 'Orders'
    item_tag_name = 'Order'


class OrderExportView(APIView):
    renderer_classes = [OrdersXMLRenderer]

    def get(self, request):
        orders = Order.objects.all()
        orders_serializer = OrderSerializer(orders, many=True)
        return Response(orders_serializer.data)


@api_view(http_method_names=["GET"])
def get_rates(request):
    basket = Basket(request)
    logger.debug(f"get_rates: Basket>\n{basket}")
    address_d = json.loads(request.session["address"])
    logger.debug(f"as a dict:\n{address_d}")
    choices = shipping_choices(basket, address_d)

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
