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
    """
    add stock to room, either creating new Stock or increasing quantity of an existing one
    """
    stock = to_room.get_stock_by_sku(sku)
    if stock:
        stock.quantity += qty
        stock.save()
        return stock

    new_stock = Stock()
    new_stock.productinv = ProductInventory.objects.get(sku=sku)
    new_stock.quantity = qty
    new_stock.room = to_room

    return new_stock


def move_stock(from_room: Room, to_room: Room, sku: str, qty: int) -> Stock:
    """
    move stocks between rooms, including to/from nowhere
    """
    assert from_room or to_room
    if not from_room:  # ex nihilo
        new_stock = add_stock(to_room, sku, qty=qty)
        new_stock.save()
        return new_stock
    elif to_room:  # both from_room and to_room both are given
        to_stock = to_room.get_stock_by_sku(sku)
        from_stock = from_room.get_stock_by_sku(sku)
        to_q_before = to_stock.quantity if to_stock else None
        f_q_before = from_stock.quantity
        if not to_stock:
            new_stock = add_stock(to_room, sku, qty=qty)
            from_stock.quantity -= qty
            from_stock.save()
            new_stock.save()
            return new_stock
        to_stock.quantity += qty
        to_stock.save()
        from_stock.quantity -= qty
        from_stock.save()
        return to_stock
    else:  # from_room given but not to_room
        from_stock = from_room.get_stock_by_sku(sku)
        from_stock.quantity -= qty
        from_stock.save()
        return None
