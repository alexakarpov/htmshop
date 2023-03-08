import logging

from .models import (
    ProductInventory,
    Room,
    Stock,
)
from ecommerce.constants import (
    MOUNTED_ICON_TYPE_NAME,
    ICON_PRINT_TYPE_NAME,
)

def padd(it, l, c=" "):
    if len(it) >= l:
        return (it, 0)

    else:
        p = l - len(it)
        return (it + (c * p), p)


def add_stock(to_room: Room, sku: str, qty: int = 0):
    new_stock = Stock()
    new_stock.product = ProductInventory.objects.get(sku=sku)
    new_stock.quantity = qty
    new_stock.room = to_room
    print(f'added {new_stock}')
    return new_stock


def move_stock(stock: Stock, to_room: Room, qty: int) -> Stock:
    try:
        to_stock = to_room.get_stock_by_sku(stock.product.sku)
    except Stock.DoesNotExist:
        to_stock = add_stock(to_room, stock.product.sku)
        assert to_stock

    to_stock.quantity += qty
    stock.quantity -= qty
    stock.save()
    to_stock.save()
    return to_stock


def clean_room(name):
        room=Room.objects.get(name__icontains=name)
        room.stock_set.all().delete()
