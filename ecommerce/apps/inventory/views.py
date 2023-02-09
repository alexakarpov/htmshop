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
    WS_SEPARATOR,
)

from ecommerce.constants import PRINT_TYPE_ID
from django.contrib.admin.views.decorators import staff_member_required

from django.shortcuts import render
from .models import ProductInventory, Room, Stock
from .utils import print_work
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
        work = work * 15  # TODO remove
        paginator = Paginator(work, 27)

        return {"work": paginator}


def move_stock_view(request):
    assert request.method == "POST", "only POST is allowed"
    logger.debug(request.POST)
    from_id = request.POST.get("from_room")
    to_id = request.POST.get("to_room")
    quantity = int(request.POST.get("qty"))
    sku = request.POST.get("sku")
    logger.debug(
        f"move request, from {from_id} to {to_id}, {quantity} of {sku}"
    )
    from_room = Room.objects.get(pk=from_id)
    to_room = Room.objects.get(pk=to_id)

    from_stock = from_room.get_stock_by_sku(sku)
    if not from_stock:
        messages.warning(
            request, "the inventory for move is missing from the source room"
        )
        return redirect("inventory:dashboard")

    fqty = from_stock.quantity
    if fqty < quantity:
        messages.warning(
            request, f"insufficient quantity ({fqty}) of {sku} in {from_room}"
        )
        return redirect("inventory:dashboard")

    else:
        from_stock.quantity -= quantity
        to_stock = to_room.get_stock_by_sku(sku)
        if to_stock:
            to_stock.quantity += quantity
        else:
            to_stock = Stock()
            to_stock.room = to_room
            to_stock.quantity = quantity
            to_stock.product = from_stock.product
        from_stock.save()
        to_stock.save()

    messages.success(
        request,
        f"moved { quantity } of { sku } fom { from_room } to { to_room }",
    )

    return render(
        request,
        "index.html",
    )


def inventory_index(request):
    form = MoveStockForm()
    rooms = Room.objects.all()
    sanding = Room.objects.get(id=1)
    # printing = Room.objects.get(id=2)
    mounting = Room.objects.get(id=2)
    painting = Room.objects.get(id=3)
    choices = []
    for r in rooms:
        c = (r.pk, r.name)
        choices.append(c)
    form.choices = choices
    return render(
        request,
        "dashboard.html",
        {
            "form": form,

            "mounting": mounting,
            "sanding": sanding,
            "painting": painting
        },
    )
