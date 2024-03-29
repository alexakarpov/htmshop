import csv, re
import sys

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.utils.text import slugify

from ecommerce.apps.catalogue.models import Product, Category


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open("ecommerce/apps/catalogue/data/catalogue.csv") as f:
            r = csv.reader(f)
            next(r, None)  # skip the first row (header)
            for row in r:
                print(f"{row[0]} - {row[1]}")
                sku_base = row[0]
                cat_name = row[1]
                cat_slug = slugify(cat_name)
                print(f"fetching category by slug '{cat_slug}'")
                category = Category.objects.get(slug=cat_slug)
                title = row[2]
                img_files = row[3]  # could be multiple, space-separated
                img_file = img_files.split(" ")[
                    0
                ]  # TODO: support multiple images
                desc = row[4]
                product_slug = slugify(title)
                slug = product_slug
                slug_n = 1
                for i in range(2, 6): # 5 with the same title/slug sounds like enough
                    try:
                        _exists = Product.objects.get(slug=slug)
                        slug_n+=1
                        slug=product_slug+str(slug_n)
                    except Product.DoesNotExist:
                        # current slug is unique
                        break

                try:
                    prod = Product.objects.create(
                        sku_base=sku_base,
                        category=category,
                        title=title,
                        slug=product_slug,
                        image=f"images/{img_file}",
                        description=desc,
                    )
                    print(f"created {prod}")

                except IntegrityError:
                    e = sys.exc_info()[0]
                    print(f"IntegrityError: object probably already exists")
