from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from ecommerce.apps.inventory.models import Stock, ProductType

from ecommerce.constants import MOUNTED_ICON_TYPE_ID


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        For example Lord Save Me as a 16 x 20 (mounted) the SKU will be A-391.16x20M
        """

        sizes = [
            "5x7",
            "11x14",
            "16x20",
            "20x24",
            "24x30",
            "30x40",
            "40x50",
        ]
        mounted_type = ProductType.objects.get(id=MOUNTED_ICON_TYPE_ID)
        for p in Stock.objects.filter(
            product_type=MOUNTED_ICON_TYPE_ID
        ):
            a_sku = p.sku
            for size in sizes:
                er_sku = a_sku + "." + size + "M"
                ps = Stock.objects.create(
                    sku=er_sku,
                    product=p.product,
                    product_type=mounted_type,
                    # restock_point=1,
                    # target_amount=1,
                    weight=0.1,
                    price=18.0,
                    spec=size
                )
