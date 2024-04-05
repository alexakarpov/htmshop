from ecommerce.apps.orders.models import Order
from pprint import pprint
from django.db.models.functions import (
    ExtractWeek,
    ExtractYear,
)
from django.db.models import Count


def run():
    orders = Order.objects.filter(items__stock__sku__startswith="A-")

    timed_sales = (
        orders.annotate(
            week=ExtractWeek("created_at"), year=ExtractYear("created_at")
        )
        .values("items__stock__sku", "week", "year")
        .annotate(
            sales=Count("*"),
        )
    )

    pprint(timed_sales)
