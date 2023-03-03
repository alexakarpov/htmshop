import logging

from .models import (
    ProductInventory,
    PrintingWorkItem,
    SandingWorkItem,
    MountingWorkItem,
    Room,
    Stock,
)
from ecommerce.constants import (
    MOUNTED_ICON_TYPE_NAME,
    ICON_PRINT_TYPE_NAME,
)

logger = logging.getLogger("django")


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

    sanding_room = Room.objects.get(name__icontains="sand")

    mounted_icons = ProductInventory.objects.filter(
        product_type__name="mounted icon"
    ).order_by("sku")

    result = []

    for it in mounted_icons:
        sku = it.sku
        w_stock = wrapping_room.get_stock_by_sku(sku)
        p_stock = painting_room.get_stock_by_sku(sku)
        s_stock = sanding_room.get_stock_by_sku(sku)
        w_qty = w_stock.quantity if w_stock else 0
        p_qty = p_stock.quantity if p_stock else 0
        s_qty = s_stock.quantity if s_stock else 0

        qty = w_qty + p_qty
        if qty < it.restock_point:
            logger.debug(
                f"below the restock point ({it.restock_point}), adding { it.target_amount - qty } to reach {it.target_amount}"
            )
            wit = SandingWorkItem(
                it.sku,
                it.product.title,
                s_qty,
                it.target_amount - qty,
            )
            result.append(wit)
        else:
            logger.debug(
                f"above the restock point ({it.restock_point}), continuing"
            )
            continue
    return result


def mounting_work():
    painting_room = Room.objects.get(name__icontains="paint")
    mounted_icons = ProductInventory.objects.filter(
        product_type__name="mounted icon"
    ).order_by("sku")
    result = []

    for it in mounted_icons:
        sku = it.sku
        p_stock = painting_room.get_stock_by_sku(sku)
        p_qty = p_stock.quantity if p_stock else 0
        
        if p_qty < it.restock_point:
            wit = MountingWorkItem(sku, it.product.title)
            result.append(wit)
    
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
