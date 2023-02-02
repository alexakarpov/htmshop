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
from .models import ProductInventory, make_fake_pinv
from .utils import filter_inventory
from django.views.generic.list import ListView

logger = logging.getLogger("console")


def ts():
    return datetime.now().strftime("%y-%m-%d")


class PrintWorkListHTMLView(ListView):
    model = ProductInventory
    paginate_by = 13

    def get_context_data(self, **kwargs):
        fakes = []
        for i in range(1, 100):
            fakes.append(make_fake_pinv())

        paginator = Paginator(fakes, 27)

        return {"work": paginator}


def generate_pdf(request):
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="hello.pdf")


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
