from django.core.management import call_command
from django.core.management.base import BaseCommand

from ecommerce.apps.inventory.models import Stock, ProductType

from ecommerce.constants import MOUNTED_ICON_TYPE_ID, ICON_PRINT_TYPE_ID


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for p in Stock.objects.filter(
            product_type=MOUNTED_ICON_TYPE_ID
        ):
            print_sku = p.sku + "P"
            print_type = ProductType.objects.get(id=ICON_PRINT_TYPE_ID)
            Stock.objects.create(
                sku=print_sku,
                product=p.product,
                product_type=print_type,
                weight=0.1,
                price=18.0,
                spec="print"
            )
