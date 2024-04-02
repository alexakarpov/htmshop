from ecommerce.apps.orders.models import Order, OrderItem
from pprint import pprint
from django.db import connection
from datetime import timedelta, datetime
from django.db.models.functions import (ExtractWeek,ExtractYear,)
from django.db.models import Sum


def run():
    # month = timedelta(days=30)

    orders=Order.objects.filter(items__stock__sku__startswith="A-")
    timed_sales=orders.annotate(week=ExtractWeek("created_at"), year=ExtractYear("created_at"), )
    # 'items__stock__price'
    # now each order has 'week' and 'year' attached to it
    sales = with_dates.annotate(overal=Sum("items__stock__price"))
        
        
    pprint(sales)
    # for s in sales:
    #     pprint(f"{s} ({s.year}/{s.week} ")

    # .values('order__created_at', 'pk')

    # pprint(connection.queries)

    # do values() call, giving a field (sku?) before annotating


# [
#     {
#         "items__stock__sku": "A-159",
#         "items__stock__price": Decimal("32.00"),
#         "week": 13,
#         "year": 2024,
#     },
#     {
#         "items__stock__sku": "A-34",
#         "items__stock__price": Decimal("32.00"),
#         "week": 13,
#         "year": 2024,
#     },
#     {
#         "items__stock__sku": "A-34",
#         "items__stock__price": Decimal("32.00"),
#         "week": 13,
#         "year": 2024,
#     },
#     {
#         "items__stock__sku": "A-159",
#         "items__stock__price": Decimal("32.00"),
#         "week": 13,
#         "year": 2024,
#     },
#     {
#         "items__stock__sku": "A-21",
#         "items__stock__price": Decimal("32.00"),
#         "week": 11,
#         "year": 2024,
#     },
#     {
#         "items__stock__sku": "A-132",
#         "items__stock__price": Decimal("32.00"),
#         "week": 1,
#         "year": 2024,
#     },
#     {
#         "items__stock__sku": "A-34",
#         "items__stock__price": Decimal("32.00"),
#         "week": 1,
#         "year": 2024,
#     },
#     {
#         "items__stock__sku": "A-399",
#         "items__stock__price": Decimal("32.00"),
#         "week": 1,
#         "year": 2024,
#     },
#     {
#         "items__stock__sku": "A-21",
#         "items__stock__price": Decimal("32.00"),
#         "week": 1,
#         "year": 2024,
#     },
#     {
#         "items__stock__sku": "A-21",
#         "items__stock__price": Decimal("32.00"),
#         "week": 52,
#         "year": 2023,
#     },
# ]
