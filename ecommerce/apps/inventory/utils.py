import logging

from .models import ProductInventory, WorkItem, Room, Stock
from ecommerce.constants import (
    MOUNTED_ICON_TYPE_NAME,
    ICON_PRINT_TYPE_NAME,
)

logger = logging.getLogger("console")


def padd(it, l, c=" "):
    if len(it) >= l:
        return (it, 0)

    else:
        p = l - len(it)
        return (it + (c * p), p)


def print_work():
    room = Room.objects.get(
        name__icontains="wrapping"
    )  # TODO: sorce from Printing?

    inventory = room.get_stock_by_type(ICON_PRINT_TYPE_NAME)

    result = []
    for it in inventory:
        if it.quantity < it.product.restock_point:
            w_qty = it.product.target_amount - it.quantity
            wit = WorkItem(
                it.product.sku,
                it.product.product.title,
                it.product.product_type.name,
                w_qty,
            )
            result.append(wit)
        else:
            continue
    return result


def add_stock(to_room: Room, sku: str, qty: int = 0):
    new_stock = Stock()
    new_stock.product = ProductInventory.objects.get(sku=sku)
    new_stock.quantity = qty
    new_stock.room = to_room
    return new_stock


def move_stock(stock: Stock, to_room: Room, qty: int) -> Stock:
    to_stock = to_room.get_stock_by_sku(stock.product.sku)
    if not to_stock:
        to_stock = add_stock(to_room, stock.product.sku)
    to_stock.quantity += qty
    stock.quantity -= qty
    stock.save()
    to_stock.save()
    return to_stock
