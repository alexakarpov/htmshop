from django.core.management import call_command
from django.core.management.base import BaseCommand
import re

from ecommerce.apps.catalogue.models import Product
from ecommerce.constants import ID_LOOKUP

LURE = '<a href="product_info\.php/products_id/(\d+)">([\w\s]+)</a>'
href_pat = re.compile(LURE)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for p in Product.objects.all():
            # pat=re.compile("product_info.php/(?:cPath/((?:\d+_)*\d+)/)?(?:products_id/(\d+))")

            m = re.search(href_pat, p.description)
            if m is not None:
                print("-" * 50)
                print(f"changing description of {p.sku_base} ({p.title})")
                print("old description:\n")
                print(p.description)
                id_in_href = int(m.group(1))
                href_title = m.group(2)
                linked_to_sku = ID_LOOKUP.get(id_in_href)
                print(
                    f"\nit refers to id {linked_to_sku}, titled {href_title}"
                )
                linked_product = Product.objects.get(sku_base=linked_to_sku)
                replacement = re.sub(
                    LURE,
                    f'<a href="/product/{linked_product.slug}">{href_title}</a>',
                    p.description,
                )

                print(f"new description:\n{replacement}")
                p.description = replacement
                p.save()
