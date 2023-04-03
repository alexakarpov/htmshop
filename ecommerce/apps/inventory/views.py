import logging

from datetime import datetime

from django.contrib import messages
from django.shortcuts import redirect

from django.core.paginator import Paginator
from ecommerce.constants import (
    ITEMS_PER_PAGE,
)

from ecommerce.constants import PRINT_TYPE_ID
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import ProductInventory, get_or_create_stock_by_sku
from .lists import (
    print_work,
    sanding_work,
    mounting_work,
    sawing_work,
)
from .utils import move_stock

from django.views.generic.list import ListView

logger = logging.getLogger("django")


def ts():
    return datetime.now().strftime("%y-%m-%d")


class PrintingWorkListView(ListView):
    model = ProductInventory
    template_name = "printing_list.html"

    def get_context_data(self, **kwargs):
        work = print_work()
        # work = work * 150  # TODO remove
        paginator = Paginator(work, ITEMS_PER_PAGE)

        return {"work": paginator, "title": "printing", "now": ts()}


class SandingWorkListView(ListView):
    model = ProductInventory
    template_name = "sanding_list.html"

    def get_context_data(self, **kwargs):
        work = sanding_work()
        # work = work * 150  # TODO remove
        paginator = Paginator(work, ITEMS_PER_PAGE)

        return {"work": paginator, "title": "sanding", "now": ts()}


class MountingWorkListView(ListView):
    model = ProductInventory
    template_name = "mounting_list.html"

    def get_context_data(self, **kwargs):
        work = mounting_work()
        # work = work * 150  # TODO remove
        paginator = Paginator(work, ITEMS_PER_PAGE)

        return {"work": paginator, "title": "mounting", "now": ts()}


class SawingWorkListView(ListView):
    model = ProductInventory
    template_name = "sawing_list.html"

    def get_context_data(self, **kwargs):
        work = sawing_work()
        paginator = Paginator(work, ITEMS_PER_PAGE)

        return {"work": paginator, "title": "sawing", "now": ts()}


def move_stock_view(request):
    assert request.method == "POST", "only POST is allowed"
    logger.debug(f"got move request, POST: {request.POST}")
    from_name = request.POST.get("from_room")
    to_name = request.POST.get("to_room")
    if from_name == to_name:
        messages.warning(
            request,
            f"what are you trying to achieve, moving from a room to itself?",
        )
        return redirect("inventory:dashboard")
    quantity = int(request.POST.get("qty"))
    sku = request.POST.get("sku")

    # sku = ProductInventory.objects.get(sku=inv_sku)
    logger.debug(
        f"move request, from {from_name} to {to_name}, {quantity} x {sku.upper()}"
    )

    move_stock(sku.upper(),
               from_room=from_name,
               to_room=to_name,
               qty=quantity)

    messages.success(
        request,
        f"moved { quantity } of { sku.upper() } from { from_name } to { to_name }",
    )

    return redirect("inventory:dashboard")


def dashboard(request):
    logger.debug(f"GET dict: {request.GET}")
    icons = ProductInventory.objects.filter(
        product_type__name="mounted icon"
    )
    skus_arr = []
    for it in icons:
        skus_arr.append(it.sku)
    skus = ",".join(skus_arr)
    sku = request.GET.get("sku")

    if sku:
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
        return render(
            request,
            "dashboard.html",
            {
                "stock": None,
                "all_skus": skus,
            })
