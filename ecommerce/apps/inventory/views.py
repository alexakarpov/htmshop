import logging
import io

from datetime import datetime
from itertools import repeat

from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.core.paginator import Paginator
from ecommerce.constants import (
    MOUNTED_ICON_TYPE_NAME,
    ICON_PRINT_TYPE_NAME,
    WS_SEPARATOR,
)

from ecommerce.constants import PRINT_TYPE_ID
from django.contrib.admin.views.decorators import staff_member_required

from django.shortcuts import render
from .models import ProductInventory
from .utils import print_work
from django.views.generic.list import ListView

logger = logging.getLogger("console")


def ts():
    return datetime.now().strftime("%y-%m-%d")


class PrintWorkListHTMLView(ListView):
    model = ProductInventory
    paginate_by = 13

    def get_context_data(self, **kwargs):
        work = print_work()
        work=work*15 #TODO remove
        paginator = Paginator(work, 27)

        return {"work": paginator}

def inventory_index(request):
    inventory = ProductInventory.objects.all()
    logger.debug(f"inventory index with {inventory.count()} productx")
    return render(
        request,
        "inventory/index.html",
        {
            "inventory": inventory,
        },
    )
