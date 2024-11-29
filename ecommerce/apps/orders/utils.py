
from ecommerce.apps.inventory.models import Stock
from ecommerce.apps.orders.models import Order


def stats(sku: str):
    s = Stock.objects.get(sku=sku)
    orders=Order.objects.all()

    print(f"found {orders.count()} orders for {s}")
