import json
import logging
from datetime import date, datetime, timedelta

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, renderer_classes

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

logger = logging.getLogger("django")


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
    print(address_d)
    logger.warn(f"address dict:\n{address_d}")
    # choices = shipping_choices_SE(basket, address_d)
    choices = shipping_choices_SS(basket, address_d)
    print(f"got {len(choices)} choices")
    for c in choices:
        print(f"choice: {c}")

    if len(choices) == 0:
        logger.error("no rates in SS response")
        return JsonResponse({"choices": []})

    tiers = split_tiers_SS(choices, address_d.get("country_code") != "US")
    if len(tiers) == 0:
        logger.error("no rates in SS response")
        return JsonResponse({"choices": []})

    logger.warn(f"Tiers are:{tiers}")
    e = sorted(tiers["express"])[0]
    r = sorted(tiers["regular"])[0]
    f = sorted(tiers["fast"])[0]
    e.name = "Expedited"
    f.name = "Fast"
    r.name = "Economy"
    serializer = ShippingChoiceSSSerializer([r, f, e], many=True)
    sdata = serializer.data
    return JsonResponse({"choices": sdata})
