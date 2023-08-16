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
        with open("ecommerce/apps/catalogue/data/products.csv") as f:
            r = csv.reader(f)
            next(r, None) # skip the first row (header)
            for row in r:
                sku_base = row[0]
                cat = row[1]  # TODO fix
                title = row[2]
                slug = row[3]
                img_file = row[4]
                desc = row[5]

                try:
                    prod = Product.objects.create(
                        sku_base=sku_base,
                        title=title,
                        slug=slug,
                        image=f"images/{img_file}",
                        description=desc,
                    )
                    print(f"created {prod}")

                except:
                    print(f"something wicked this way came!")
