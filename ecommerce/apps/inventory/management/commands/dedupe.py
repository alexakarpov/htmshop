from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from ecommerce.apps.inventory.models import Stock, ProductInventory, get_or_create_stock_by_sku

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for p in ProductInventory.objects.filter(
        product_type__name="mounted icon"):
            print(p.sku)

            try:
                stock = get_or_create_stock_by_sku(p.sku)
            except Stock.MultipleObjectsReturned:
                print(f"{p.sku} has multiple stock records...")
                first_pk = Stock.objects.filter(productinv__sku=p.sku).first().pk
                Stock.objects.filter(productinv__sku=p.sku).exclude(pk=first_pk).delete()


                
        