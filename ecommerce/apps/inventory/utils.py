import logging

from .models import (
    ProductInventory,
    Stock,
    get_stock_by_sku,
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


def move_stock(from_room: str, to_room: str, sku: str, qty: int) -> Stock:
    """
    move stocks between rooms, including to/from nowhere
    """
    assert from_room or to_room, "at least one room must be provided"
    print(
        f"moving {sku}x{qty} from {from_room or 'nowhere'} to {to_room or 'nowhere'}")
    stock = get_stock_by_sku(sku)

    if not stock:
        stock = Stock()
        pinv = ProductInventory.objects.get(sku=sku)
        stock.productinv = pinv

    stock.settle_quantities(qty, from_room, to_room)
    stock.save()
    stock.refresh_from_db()
    print(f"after move: {stock}")
    return stock
