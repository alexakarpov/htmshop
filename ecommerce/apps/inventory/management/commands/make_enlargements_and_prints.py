from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from ecommerce.apps.inventory.models import Stock, ProductType
from ecommerce.apps.catalogue.models import Product, Category

from ecommerce.constants import (
    MOUNTED_ICON_TYPE_ID,
    ICONS_CATEGORY_ID,
    ICON_PRINT_TYPE_ID,
)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        For example Lord Save Me as a 16 x 20 (mounted) the SKU will be A-391.16x20M
        """

        # standard 8x10 is 1 pound 10 oz (26 oz)
        sizes = [
            ("5x7", 11, 16),
            ("11x14", 22, 32),
            ("16x20", 33, 52),
            ("20x24", 33, 76),
            ("24x30", 55, 80)("30x40", 66, 92),
            ("40x50", 77, 110),
        ]
        mounted_type = ProductType.objects.get(id=MOUNTED_ICON_TYPE_ID)
        print_type = ProductType.objects.get(id=ICON_PRINT_TYPE_ID)

        icons_parent_category = Category.objects.get(id=ICONS_CATEGORY_ID)
        icons = []
        for cat in icons_parent_category.get_family():
            for product in cat.product_set.all():
                icons.append(product)

        for icon in icons:
            a_sku = icon.sku_base
            # enlargements
            for size, price, weight in sizes:
                er_sku = a_sku + "." + size + "M"
                try:
                    Stock.objects.create(
                        sku=er_sku,
                        product=icon,
                        product_type=mounted_type,
                        weight=weight,
                        price=price,
                        spec=size,
                    )
                except DatabaseError:
                    print(f"SKU {er_sku} already exists")
            # prints
            print_sku = a_sku + "P"
            try:
                Stock.objects.create(
                    sku=print_sku,
                    product=icon,
                    product_type=print_type,
                    weight=0.1,
                    price=18.0,
                    spec="print",
                )
            except DatabaseError:
                print(f"SKU {print_sku} already exists")
