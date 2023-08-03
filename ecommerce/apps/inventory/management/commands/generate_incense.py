from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import DatabaseError
from ecommerce.apps.catalogue.models import Category

from ecommerce.apps.inventory.models import Stock, ProductType

from ecommerce.constants import INCENSE_CATEGORY_ID, INCENSE_TYPE_ID


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        # TODO: account for incense classes+prices
        sizes = [
            ("A", 17, 22),
            ("B", 9, 11),
            ("C", 1.5, 5),
        ]
        incense_type = ProductType.objects.get(id=INCENSE_TYPE_ID)
        incense_parent_category = Category.objects.get(id=INCENSE_CATEGORY_ID)
        incenses = []

        for cat in incense_parent_category.get_family():
            for product in cat.product_set.all():
                incenses.append(product)

        for p in incenses:
            i_sku = p.sku_base
            for size, weight, price in sizes:
                is_sku = i_sku + size
                try:
                    Stock.objects.create(
                        sku=is_sku,
                        product=p,
                        product_type=incense_type,
                        weight=weight,
                        price=price,
                        spec=size,
                    )
                except DatabaseError:
                    print(f"SKU {is_sku} already exists")
