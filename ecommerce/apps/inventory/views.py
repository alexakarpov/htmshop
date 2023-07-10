import logging
from datetime import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.html import escape
from django.views.generic.list import ListView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ecommerce.constants import LINES_PER_PAGE, PRINT_TYPE_ID

from .lists import mounting_work, print_work, sanding_work, sawing_work
from .models import ProductStock, get_or_create_stock_by_sku
from .serializers import ProductStockSerializer
from .utils import (
    move_sku_from_print_supply,
    move_sku_to_print_supply,
    move_stock_one_sku,
)

logger = logging.getLogger("django")


def ts():
    return datetime.now().strftime("%y-%m-%d")


class PrintingWorkListView(ListView):
    model = ProductStock
    template_name = "printing_list.html"

    def get_context_data(self, **kwargs):
        work = print_work()
        paginator = Paginator(work * 20, LINES_PER_PAGE)

        return {"work": paginator, "title": "printing", "now": ts()}


class SandingWorkListView(ListView):
    model = ProductStock
    template_name = "sanding_list.html"

    def get_context_data(self, **kwargs):
        work = sanding_work()
        # work = work * 150  # TODO remove
        paginator = Paginator(work, LINES_PER_PAGE)

        return {"work": paginator, "title": "sanding", "now": ts()}


class MountingWorkListView(ListView):
    model = ProductStock
    template_name = "mounting_list.html"

    def get_context_data(self, **kwargs):
        work = mounting_work()
        # work = work * 150  # TODO remove
        paginator = Paginator(work, LINES_PER_PAGE)

        return {"work": paginator, "title": "mounting", "now": ts()}


class SawingWorkListView(ListView):
    model = ProductStock
    template_name = "sawing_list.html"

    def get_context_data(self, **kwargs):
        work = sawing_work()
        paginator = Paginator(work, LINES_PER_PAGE)

        return {"work": paginator, "title": "sawing", "now": ts()}


@api_view(["POST"])
def inspect_sku(request):
    data = request.POST
    sku = escape(data.get("sku").upper())
    logger.error(sku)
    logger.debug(f"inspecting {sku}")
    item = ProductStock.objects.get(sku=sku)
    psupp = item.get_print_supply_count()
    serializer = ProductStockSerializer(item, many=False)
    sdata = serializer.data
    sdata["psupp"] = psupp
    logger.debug(f"API data: {sdata}")
    return JsonResponse(sdata)


@api_view(["POST"])
def move_stock(request):
    logger.debug(f"got move request, POST: {request.POST}")
    from_name = request.POST.get("from_room")
    to_name = request.POST.get("to_room")
    quantity = int(request.POST.get("qty"))
    sku = request.POST.get("sku").upper()

    if to_name.find("print") >= 0:
        stock = move_sku_to_print_supply(sku, from_name, qty=quantity)
    elif from_name.find("print") >= 0:
        stock = move_sku_from_print_supply(sku, to_name, quantity)
    else:
        move_stock_one_sku(
            sku, from_room=from_name, to_room=to_name, qty=quantity
        )

    item = ProductStock.objects.get(sku=sku)
    psupp = item.get_print_supply_count()
    serializer = ProductStockSerializer(item, many=False)
    sdata = serializer.data
    sdata["psupp"] = psupp
    logger.debug(f"API data: {sdata}")
    return JsonResponse(sdata)


def dashboard(request):
    logger.debug(f"GET dict: {request.GET}")
    logger.debug(f"POST dict: {request.POST}")

    icons = ProductStock.objects.filter(product_type__name="mounted icon")
    skus_arr = []
    for it in icons:
        skus_arr.append(it.sku)
    skus = ",".join(skus_arr)
    sku = request.GET.get("sku")

    if sku:
        logger.debug(f"a SKU was provided: {sku}")
        sku = sku.upper()
        logger.debug(f"inspecting {sku}")
        stock = get_or_create_stock_by_sku(sku)
        return render(
            request,
            "dashboard.html",
            {
                "all_skus": skus,
                "stock": stock,
            },
        )
    else:
        logger.debug(f"a SKU was not provided")
        return render(
            request,
            "dashboard.html",
            {
                "stock": None,
                "all_skus": skus,
            },
        )
