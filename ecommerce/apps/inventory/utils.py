import logging

from .models import ProductInventory, PrintingWorkItem, SandingWorkItem, Room, Stock
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
        name__icontains="wrap"
    )  # TODO: sorce from Printing?

    inventory = room.get_stock_by_type(ICON_PRINT_TYPE_NAME)

    result = []
    for it in inventory:
        if it.quantity < it.product.restock_point:
            w_qty = it.product.target_amount - it.quantity
            wit = PrintingWorkItem(
                it.product.sku,
                it.product.product.title,
                w_qty,
            )
            result.append(wit)
        else:
            continue
    return result


def sanding_work():
    wrapping_room = Room.objects.get(name__icontains="wrapping")

    painting_room = Room.objects.get(name__icontains="paint")

    mounted_icons = ProductInventory.objects.filter(
        product_type__name="mounted icon"
    )
    result = []
    for it in mounted_icons:
        logger.debug("######" * 2)
        sku = it.sku
        logger.debug(f"considering {sku}")
        w_stock = wrapping_room.get_stock_by_sku(sku)
        p_stock = painting_room.get_stock_by_sku(sku)
        w_qty = w_stock.quantity if w_stock else 0
        logger.debug(f"wrapping room has {w_qty} of {sku}")
        p_qty = p_stock.quantity if p_stock else 0
        logger.debug(f"painting room has {p_qty} of {sku}")
        qty = w_qty + p_qty
        logger.debug(f"qty for {sku} determined as {qty}")
        if qty < it.restock_point:
            logger.debug(f"below the restock point ({it.restock_point}), adding to reach {it.target_amount}")
            wit = SandingWorkItem(
                it.sku,
                it.product.title,
                it.target_amount - qty,
            )
            logger.debug(f"adding {wit} to the list")
            result.append(wit)
        else:
            logger.debug(f"above the restock point ({it.restock_point}), continuing")
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
