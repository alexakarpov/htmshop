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


def generate_icons(icons):
    mounted_type = ProductType.objects.get(id=MOUNTED_ICON_TYPE_ID)
    print_type = ProductType.objects.get(id=ICON_PRINT_TYPE_ID)
    print(f"generating inventory for {len(icons)} icons")

    sizes = [
        ("5x7", 32, 16),
        ("8x10", 32, 26), # the only one which is not a guess
        ("11x14", 75, 32),
        ("16x20", 100, 52),
        ("20x24", 140, 76),
        ("24x30", 190, 80),
        ("30x40", 300, 92),
        ("40x50", 625, 110),
    ]

    print_sizes = [
        ("5x7", 18, 0.1),
        ("8x10", 18, 0.1),
        ("11x14", 75, 0.2),
        ("16x20", 100, 0.2),
        ("20x24", 140, 0.3),
        ("24x30", 190, 0.5),
        ("30x40", 300, 0.7),
        ("40x50", 625, 0.9),
    ]

    pcount = ecount = 0
    for icon in icons:
        a_sku = icon.sku_base
        print(f"...for {a_sku}")
        # enlargements
        print(f"enlargements:")
        
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
                print(f"created {er_sku}")
                ecount += 1
            except DatabaseError:
                print(f"SKU {er_sku} already exists")

        # prints
        print(f"prints:")

        for size, price, weight in print_sizes:
            print_sku = a_sku + "." + size + "P"
            try:
                Stock.objects.create(
                    sku=print_sku,
                    product=icon,
                    product_type=print_type,
                    weight=weight,
                    price=price,
                    spec=f"{size} print",
                )
                print(f"created {print_sku}")
                pcount += 1
            except DatabaseError:
                print(f"SKU {print_sku} already exists")

    return ecount, pcount


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        For example Lord Save Me as a 16 x 20 (mounted) the SKU will be A-391.16x20M
        """

        icons_parent_category = Category.objects.get(id=ICONS_CATEGORY_ID)
        icons = []
        for cat in icons_parent_category.get_family():
            print(f"found category {cat} with {cat.product_set.count()} products")
            for product in cat.product_set.all():
                icons.append(product)
        e, p = generate_icons(icons)
        print(f"DONE;generated {e} enlargements and {p} prints")
