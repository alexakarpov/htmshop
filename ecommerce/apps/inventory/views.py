import logging
from datetime import datetime

from wkhtmltopdf.views import PDFTemplateResponse
from wkhtmltopdf.views import PDFTemplateView

from ecommerce.constants import PRINT_TYPE_ID
from django.contrib.admin.views.decorators import staff_member_required


from django.shortcuts import render
from .models import ProductInventory
from .utils import print_work, mount_work, header

logger = logging.getLogger("console")


def ts():
    return datetime.now().strftime("%y-%m-%d")


class PrintWorkListPDFView(PDFTemplateView):
    filename = f"list-print-{ts()}.pdf"
    template_name = "inventory/print_worklist.html"
    inventory = (
        ProductInventory.objects.filter(product_type=PRINT_TYPE_ID)
        .exclude(sku__icontains="x")
        .exclude(sku__icontains=".")
    )

    def get(self, request):

        response = PDFTemplateResponse(
            self.request,
            self.template_name,
            filename=self.filename,
            context={"work": self.inventory},
            cmd_options={"margin-top": 50},
        )
        return response


class MountWorkListPDFView(PDFTemplateView):
    filename = f"lisst-mount-{ts()}.pdf"
    template_name = "inventory/mount_worklist.html"
    inventory = ProductInventory.objects.filter(product_type=3)

    def get(self, request):

        response = PDFTemplateResponse(
            self.request,
            self.template_name,
            filename=self.filename,
            context={"work": self.inventory},
            cmd_options={"margin-top": 50},
        )
        return response


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
