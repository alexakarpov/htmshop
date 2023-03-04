import logging

from ecommerce.apps.inventory.models import (
    MountingWorkItem,
    PrintingWorkItem,
    ProductInventory,
    Room,
    SandingWorkItem,
)
from ecommerce.constants import ICON_PRINT_TYPE_NAME

logger = logging.getLogger("django")


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
        painting_stock = painting_room.get_stock_by_sku(sku)
        painting_qty = painting_stock.quantity if painting_stock else 0

        if painting_qty < it.restock_point:
            wit = MountingWorkItem(sku, it.product.title)
            result.append(wit)

    return result


def sawing_work():
    sanding_room = Room.objects.get(name__icontains="sand")
    wrapping_room = Room.objects.get(name__icontains="wrapping")
    mounted_icons = ProductInventory.objects.filter(
        product_type__name="mounted icon"
    ).order_by("sku")
    print_supply = wrapping_room.get_stock_by_type(ICON_PRINT_TYPE_NAME)
    
    result = []

    for it in mounted_icons:
        sku = it.sku
        sanding_stock = sanding_room.get_stock_by_sku(sku)
        sanding_qty = sanding_stock.quantity if sanding_stock else 0
        print = print_supply.get(product__sku=sku) # what if there's more than 1 entry?
        # or what if the stock matching the query does not exist? self.model.DoesNotExist
        print_qty = print.quantity if print else 0
        if sanding_qty < it.restock_point:
            wit = SandingWorkItem(
                sku,
                it.product.title,
                print_qty,
                it.target_amount - sanding_qty,
            )
            result.append(wit)

    return result
