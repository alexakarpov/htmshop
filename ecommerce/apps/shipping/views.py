import json
import logging
from datetime import date, datetime, timedelta

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, renderer_classes

from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.orders.models import Order
from ecommerce.apps.shipping.choice import split_tiers
from ecommerce.apps.shipping.engine import shipping_choices
from ecommerce.constants import SS_DT_FORMAT

from .serializers import ShippingChoiceSerializer
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
    logger.warn(f"as a dict:\n{address_d}")
    choices = shipping_choices(basket, address_d)

    if len(choices) == 0:
        logger.warn("no rates in SE response?")
        return JsonResponse({"choices": []})

    # print(f"CHOICES: {choices}")
    tiers = split_tiers(choices)
    # print(f"TIERS: {tiers}")

    e = sorted(tiers["express"])[0]
    r = sorted(tiers["regular"])[0]
    f = sorted(tiers["fast"])[0]
    e.name = "Expedited"
    f.name = "Fast"
    r.name = "Economy"
    serializer = ShippingChoiceSerializer([r, f, e], many=True)
    sdata = serializer.data
    return JsonResponse({"choices": sdata})
