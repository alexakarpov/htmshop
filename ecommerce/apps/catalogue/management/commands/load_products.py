import csv, re
import sys

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.utils.text import slugify

from ecommerce.apps.catalogue.models import Product, Category
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
            next(r, None)  # skip the first row (header)
            for row in r:
                sku_base = row[0]
                cat_name = row[1]
                cat_slug = slugify(cat_name)
                category=Category.objects.get(slug=cat_slug)
                title = row[2]
                slug = row[3].lower()
                img_file = row[4]
                desc = row[5]

                try:
                    prod = Product.objects.create(
                        sku_base=sku_base,
                        category=category,
                        title=title,
                        slug=slug,
                        image=f"images/{img_file}",
                        description=desc,
                    )
                    print(f"created {prod}")

                except IntegrityError:
                    e = sys.exc_info()[0]
                    print(f"IntegrityError: object probably already exists")
