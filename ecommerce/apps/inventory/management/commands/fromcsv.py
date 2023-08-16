import csv, re
from decimal import Decimal
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from ecommerce.apps.inventory.models import Stock
from ecommerce.apps.catalogue.models import Product
from ecommerce.constants import SKU_REGEX


def get_sku_base(sku):
    print(f"getting base from {sku}")
    pat = re.compile(SKU_REGEX)
    m = pat.match(sku)
    return m.group(1)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open("ecommerce/apps/inventory/data/weight_list.csv") as f:
            r = csv.reader(f)
            next(r, None)
            i = 0
            for row in r:
                sku = row[0]
                base = get_sku_base(sku)

                try:
                    prod = Product.objects.get(pk=base)
                    print("========")
                    print(prod)
                    s = Stock.objects.create(sku=base + str(i))
                    s.weight = Decimal(row[2]) * 16  # something's not right
                    s.save()
                except Product.DoesNotExist:
                    print(f"Product {base} does not exist")
