import re, csv, sys

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, IntegrityError
from ecommerce.apps.catalogue.models import Product

from ecommerce.apps.inventory.models import Stock
from ecommerce.constants import (
    BHJR_RE,
    NEW_RE,
    INCENSE_RE,
)


def process_row(row, pattern: str):
    print("row is:")
    print(row)
    print("^^^^^^^^^^^^^")
    sku = row[0]
    m = re.match(pattern, sku)
    base = m.group(1)
    print(f"looking up a Product with base {base}")
    spec = row[1]
    weight = row[2]
    restock_point = row[3]
    target_amount = row[4]
    price = row[5]

    try:
        catalogue_product = Product.objects.get(sku_base=base)
    except Product.DoesNotExist:
        sys.stderr.write(f"Product {base} not found\n")
        return -1

    try:
        stock = Stock.objects.create(
            product=catalogue_product,
            spec=spec,
            sku=sku,
            restock_point=restock_point,
            target_amount=target_amount,
            weight=weight,
            price=price,
        )
        print(f"created {stock}")
    except IntegrityError as e:
        sys.stderr.write(
            f"looks like a Stock record for {sku} already exists\n"
        )


def load_icons_stock():
    with open("ecommerce/apps/inventory/data/a-series.csv") as f:
        r = csv.reader(f)
        next(r, None)  # skip the first row (header)

        for row in r:
            process_row(row, NEW_RE)


def load_incense_stock():
    with open("ecommerce/apps/inventory/data/incense-stocks.csv") as f:
        r = csv.reader(f)
        next(r, None)  # skip the first row (header)

        for row in r:
            process_row(row, INCENSE_RE)


def load_BHJR():
    with open("ecommerce/apps/inventory/data/BHJR.csv") as f:
        r = csv.reader(f)
        next(r, None)  # skip the first row (header)

        for row in r:
            process_row(row, BHJR_RE)


def load_DGM():
    with open("ecommerce/apps/inventory/data/DGM.csv") as f:
        r = csv.reader(f)
        next(r, None)  # skip the first row (header)

        for row in r:
            print("processing a row")
            process_row(row, NEW_RE)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        ...Lord Save Me as a 16 x 20 (mounted) the SKU will be A-391.16x20M
        """
        # load_icons_stock()
        # load_incense_stock()
        # load_BHJR()
        load_DGM()
