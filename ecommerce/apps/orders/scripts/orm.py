from ecommerce.apps.orders.models import Order
from pprint import pprint
from django.db.models.functions import (
    ExtractWeek,
    ExtractYear,
)
from django.db.models import Count


def run():
    orders = Order.objects.filter(items__sku__startswith="A-")


#    timed_sales = (
#        orders.annotate(
#            week=ExtractWeek("created_at"),
#            year=ExtractYear("created_at")
#        )
#        .values("items__sku", "week", "year")
#        .annotate(
#            sales=Count("*"),
#            sku={items__sku: items__sku.quantity}
#        )
#    )

#    pprint(timed_sales)
    return
