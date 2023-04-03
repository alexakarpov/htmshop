from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from ecommerce.apps.inventory.models import Stock


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for p in Stock.objects.filter(
                product_type__name="mounted icon"):
            # print(f"--- working with {p.sku} ---")
            print_sku = p.sku+'P'
            try:
                pr = Stock.objects.get(sku=print_sku)

            except Stock.DoesNotExist:
                print(f">>>> creating a new Inventory record: {p.sku}'s print SKU<<<")
                
