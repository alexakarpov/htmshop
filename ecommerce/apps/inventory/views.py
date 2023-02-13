import logging

from datetime import datetime

from django.contrib import messages
from django.shortcuts import redirect

# from django.http import FileResponse
# from reportlab.pdfgen import canvas

from django.core.paginator import Paginator
from ecommerce.constants import (
    MOUNTED_ICON_TYPE_NAME,
    ICON_PRINT_TYPE_NAME,
    ITEMS_PER_PAGE,
)

from ecommerce.constants import PRINT_TYPE_ID
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import ProductInventory, Room, Stock
from .utils import print_work, move_stock
from .forms import MoveStockForm
from django.views.generic.list import ListView

logger = logging.getLogger("console")


def ts():
    return datetime.now().strftime("%y-%m-%d")


class PrintWorkListHTMLView(ListView):
    model = ProductInventory
    paginate_by = 13

    def get_context_data(self, **kwargs):
        work = print_work()
        # work = work * 150  # TODO remove
        paginator = Paginator(work, ITEMS_PER_PAGE)
        logger.debug(f"work: {work}")
        return {"work": paginator,
                "now": ts()}


def move_stock_view(request):
    assert request.method == "POST", "only POST is allowed"
    logger.debug(f"got move request, POST: {request.POST}")
    from_name = request.POST.get("from_room")
    to_name = request.POST.get("to_room")
    quantity = int(request.POST.get("qty"))
    inv_id = request.POST.get("sku")
    sku = ProductInventory.objects.get(pk=inv_id).sku
    logger.debug(
        f"move request, from {from_name} to {to_name}, {quantity} x {sku}"
    )
    from_room = Room.objects.get(name__icontains=from_name)
    to_room = Room.objects.get(name__icontains=to_name)

    from_stock = from_room.get_stock_by_sku(sku)
    if not from_stock:
        messages.warning(request, f"{sku} is missing from {from_room}")
        return redirect("inventory:dashboard")

    fqty = from_stock.quantity
    if fqty < quantity:
        messages.warning(
            request, f"insufficient quantity ({fqty}) of {sku} in {from_room}"
        )
        return redirect("inventory:dashboard")

    move_stock(from_stock, to_room, quantity)

    messages.success(
        request,
        f"moved { quantity } of { sku } fom { from_room } to { to_room }",
    )

    return redirect("inventory:dashboard")


def dashboard(request):
    form = MoveStockForm()
    sanding = Room.objects.get(name__icontains="Sanding")
    mounting = Room.objects.get(name__icontains="Mounting")
    painting = Room.objects.get(name__icontains="Painting")
    wrapping = Room.objects.get(name__icontains="wrapping")
    return render(
        request,
        "dashboard.html",
        {
            "form": form,
            "wrapping": wrapping,
            "painting": painting,
            "mounting": mounting,
            "sanding": sanding,
        },
    )
