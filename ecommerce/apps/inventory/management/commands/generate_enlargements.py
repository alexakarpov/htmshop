from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from ecommerce.apps.inventory.models import Stock, ProductType
from ecommerce.apps.catalogue.models import Product, Category

from ecommerce.constants import MOUNTED_ICON_TYPE_ID, ICONS_CATEGORY_ID


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        For example Lord Save Me as a 16 x 20 (mounted) the SKU will be A-391.16x20M
        """

        sizes = [
            ("5x7", 11),
            ("11x14", 22),
            ("16x20", 33),
            ("20x24", 33),
            ("24x30", 55),
            ("30x40", 66),
            ("40x50", 77),
        ]
        mounted_type = ProductType.objects.get(id=MOUNTED_ICON_TYPE_ID)
        icons_parent_category = Category.objects.get(id=ICONS_CATEGORY_ID)
        icons = []
        for cat in icons_parent_category.get_family():
            for product in cat.product_set.all():
                icons.append(product)
        
        for p in icons:
            a_sku = p.sku_base
            for size, pr in sizes:
                    er_sku = a_sku + "." + size + "M"
                    try:
                        Stock.objects.create(
                            sku=er_sku,
                            product=p,
                            product_type=mounted_type,
                            weight=0.1,
                            price=pr,
                            spec=size,
                        )
                    except DatabaseError:
                        print(f"SKU {er_sku} already exists")
