import logging

from datetime import datetime

from django.contrib import messages
from django.shortcuts import redirect

# from django.http import FileResponse
# from reportlab.pdfgen import canvas

from django.core.paginator import Paginator
from ecommerce.constants import (
    ITEMS_PER_PAGE,
)

from ecommerce.constants import PRINT_TYPE_ID
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import ProductInventory, Room, Stock
from .lists import (
    print_work,
    sanding_work,
    mounting_work,
    sawing_work,
)
from .utils import move_stock

from django.views.generic.list import ListView

logger = logging.getLogger("console")


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
    inv_sku = request.POST.get("sku")
    sku = ProductInventory.objects.get(sku=inv_sku)
    logger.debug(
        f"move request, from {from_name} to {to_name}, {quantity} x {inv_sku}"
    )
    from_room = Room.objects.get(
        name__icontains=from_name) if from_name != "nihil" else None
    to_room = Room.objects.get(
        name__icontains=to_name) if to_name != "nihil" else None

    move_stock(from_room, to_room, inv_sku, qty=quantity)

    messages.success(
        request,
        f"moved { quantity } of { sku } fom { from_room } to { to_room }",
    )

    return redirect("inventory:dashboard")


def dashboard(request):
    sanding = Room.objects.get(name__icontains="Sanding")
    painting = Room.objects.get(name__icontains="Painting")
    wrapping = Room.objects.get(name__icontains="wrapping")
    rooms = [
        wrapping,
        painting,
        sanding,
    ]  # the order of the rooms _must_ be this
    icons = ProductInventory.objects.filter(
        product_type__name="mounted icon"
    )

    skus_arr = []
    for it in icons:
        skus_arr.append(it.sku)
    
    skus = ",".join(skus_arr)

    logger.debug(f"skus: {skus}")
    return render(
        request,
        "dashboard.html",
        {"rooms": rooms,
         "all_skus": skus},
    )
