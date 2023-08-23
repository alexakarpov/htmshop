import re, csv

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError
from ecommerce.apps.catalogue.models import Product

from ecommerce.apps.inventory.models import ProductType, Stock
from ecommerce.constants import SKU_REGEX, NEW_RE, ICON_PRINT_TYPE_ID, MOUNTED_ICON_TYPE_ID


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        ...Lord Save Me as a 16 x 20 (mounted) the SKU will be A-391.16x20M
        """
        mounted_icon = ProductType.objects.get(id=MOUNTED_ICON_TYPE_ID)
        icon_print = ProductType.objects.get(id=ICON_PRINT_TYPE_ID)
        with open("ecommerce/apps/inventory/data/stocks.csv") as f:
            r = csv.reader(f)
            next(r, None)  # skip the first row (header)
            pat = re.compile(NEW_RE)
            for row in r:
                print(f"processing: {row}")
                sku = row[0]
                m=re.match(pat, sku)
                base = m.group(1)
                spec = row[1]
                weight = row[2]
                restock_point = row[3]
                target_amount = row[4]
                price = row[5]
                
                match sku[-1]:
                    case "M":
                        type = mounted_icon
                    case "P":
                        type = icon_print
                    case _: # "A-1" without M/P can be a stock item's SKU, 8x10 mounted is implied
                        type = mounted_icon
                       
                try:
                    catalogue_product = Product.objects.get(sku_base=base)
                except Product.DoesNotExist:
                    print(f"Product {base} not found")
                    continue

                try:
                    stock = Stock.objects.create(
                        product = catalogue_product,
                        product_type = type,
                        spec = spec,
                        sku = sku,
                        restock_point = restock_point,
                        target_amount = target_amount,
                        weight = weight

                    )
                    print(f"created {stock}")

                except:
                    print(f"boom")
