import re, csv

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, IntegrityError
from ecommerce.apps.catalogue.models import Product

from ecommerce.apps.inventory.models import ProductType, Stock
from ecommerce.constants import (
    INCENSE_TYPE_ID,
    SKU_REGEX,
    NEW_RE,
    ICON_PRINT_TYPE_ID,
    MOUNTED_ICON_TYPE_ID,
    INCENSE_RE,
)

mounted_icon_type = ProductType.objects.get(id=MOUNTED_ICON_TYPE_ID)
icon_print = ProductType.objects.get(id=ICON_PRINT_TYPE_ID)
incense_type = ProductType.objects.get(id=INCENSE_TYPE_ID)


def process_row(row, pattern, stock_type):
    print(f"processing: {row} with pattern {pattern}")
    sku = row[0]
    m = re.match(pattern, sku)
    base = m.group(1)
    print(f"looking up a Product with base {base}")
    spec = row[1]
    weight = row[2]
    restock_point = row[3]
    target_amount = row[4]
    price = row[5]
    type = stock_type
    try:
        catalogue_product = Product.objects.get(sku_base=base)
    except Product.DoesNotExist:
        print(f"Product {base} not found")
        return -1

    try:
        stock = Stock.objects.create(
            product=catalogue_product,
            product_type=stock_type,
            spec=spec,
            sku=sku,
            restock_point=restock_point,
            target_amount=target_amount,
            weight=weight,
            price=price,
        )
        print(f"created {stock}")
    except IntegrityError as e:
        print(f"looks like a Stock record for {sku} already exists")


def load_icons_stock():
    with open("ecommerce/apps/inventory/data/a-series.csv") as f:
        r = csv.reader(f)
        next(r, None)  # skip the first row (header)

        for row in r:
            process_row(row, NEW_RE, mounted_icon_type)


def load_incense_stock():
    with open("ecommerce/apps/inventory/data/incense-stocks.csv") as f:
        r = csv.reader(f)
        next(r, None)  # skip the first row (header)

        for row in r:
            process_row(row, INCENSE_RE, incense_type)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        ...Lord Save Me as a 16 x 20 (mounted) the SKU will be A-391.16x20M
        """
        load_icons_stock()
        load_incense_stock()
