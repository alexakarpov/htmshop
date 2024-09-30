import json
import logging
from datetime import date, datetime, timedelta

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view

# ,renderer_classes

from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.orders.models import Order
from ecommerce.apps.shipping.choice import split_tiers_SE, split_tiers_SS
from ecommerce.apps.shipping.engine import (
    shipping_choices_SE,
    shipping_choices_SS,
)

from ecommerce.constants import SS_DT_FORMAT

from .serializers import ShippingChoiceSESerializer, ShippingChoiceSSSerializer
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@csrf_exempt
def shipstation(request):
    if request.method == "GET":
        action = request.GET.get("action")
        # assert action == "export"
        start_date_str = request.GET.get("start_date") or (
            date.today() - timedelta(days=30)
        ).strftime(SS_DT_FORMAT)

        end_date_str = request.GET.get("end_date") or date.today().strftime(
            SS_DT_FORMAT
        )

        start_date = datetime.strptime(start_date_str, SS_DT_FORMAT)

        end_date = datetime.strptime(end_date_str, SS_DT_FORMAT)

        orders = Order.objects.filter(
            updated_at__gte=start_date, updated_at__lte=end_date
        )

        return render(
            request,
            "shipping/orders.xml",
            {"orders": orders},
            content_type="text/xml",
        )

    elif request.method == "POST":
        action = request.GET.get("action")
        order_number = request.GET.get("order_number")
        assert action == "shipnotify"
        try:
            order = Order.objects.get(id=order_number)
            order.status = "SHIPPED"
            order.save()
        except Exception:
            return HttpResponse(status=400)

        return HttpResponse(status=200)


@api_view(http_method_names=["GET"])
def get_rates(request):
    basket = Basket(request)
    address_d = json.loads(request.session["address"])
    print("GERONIMO!")
    logger.warning(f"address dict:\n{address_d}")
    if settings.SE_ENABLED:
        choices = shipping_choices_SE(basket, address_d)
    else:
        choices = shipping_choices_SS(basket, address_d)
    if choices and len(choices) == 0:
        logger.error("no rates in response?")
        return JsonResponse({"choices": []})

    tiers = split_tiers_SE(choices, intl=address_d.get("country_code") != "US")
    if len(tiers) == 0:
        logger.error("no rates in SS/SE response")
        return JsonResponse({"choices": []})

    logger.warning(f"Tiers are:{tiers}")
    all = []
    for v in tiers.values():
        all += v
    if all:
        e = sorted(tiers["express"])[0]
        r = sorted(tiers["regular"])[0]
        f = sorted(tiers["fast"])[0]
        # careful, magic words
        e.name = "Express"
        f.name = "Fast"
        r.name = "Regular"
        serializer = ShippingChoiceSESerializer([r, f, e], many=True)
        sdata = serializer.data
        return JsonResponse({"choices": sdata})
    else:
        return JsonResponse({"choices": []})
