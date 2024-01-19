import json
import logging
from datetime import date, datetime, timedelta

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_xml.renderers import XMLRenderer

from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.orders.models import Order
from ecommerce.apps.shipping.choice import split_tiers
from ecommerce.apps.shipping.engine import shipping_choices
from ecommerce.constants import SS_DT_FORMAT

from .serializers import OrderSerializer, ShippingChoiceSerializer

logger = logging.getLogger("django")


class OrdersXMLRenderer(XMLRenderer):
    root_tag_name = "Orders"
    item_tag_name = "Order"


class OrderExportView(APIView):
    renderer_classes = [OrdersXMLRenderer]

    def get(self, request):
        print(f"SS GET, action={request.GET.get('action')}, page={request.GET.get('page')}")
        start_date_str = request.GET.get("start_date") or (
            date.today() - timedelta(days=1)
        ).strftime(SS_DT_FORMAT)
        end_date_str = request.GET.get("end_date") or date.today().strftime(SS_DT_FORMAT)
        start_date = datetime.strptime(start_date_str, SS_DT_FORMAT)
        end_date = datetime.strptime(end_date_str, SS_DT_FORMAT)

        orders = Order.objects.filter(updated_at__gte=start_date, updated_at__lte=end_date)
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
