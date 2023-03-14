import logging

from ecommerce.apps.inventory.models import (
    MountingWorkItem,
    PrintingWorkItem,
    SawingWorkItem,
    ProductInventory,
    Room,
    SandingWorkItem,
)
from ecommerce.constants import ICON_PRINT_TYPE_NAME

logger = logging.getLogger("django")


def print_work():
    room = Room.objects.get(
        name__icontains="wrap"
    )
    # this is the "Print Supply" for all SKUs
    inventory = room.get_stock_by_type(ICON_PRINT_TYPE_NAME)

    result = []
    for it in inventory:
        if it.quantity < it.productinv.restock_point:
            w_qty = it.productinv.target_amount - it.quantity
            wit = PrintingWorkItem(
                it.productinv.sku,
                it.productinv.product.title,
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
    sanding_room = Room.objects.get(name__icontains="sand")
    mounted_icons = ProductInventory.objects.filter(
        product_type__name="mounted icon"
    ).order_by("sku")
    result = []

    for it in mounted_icons:
        sku = it.sku
        sanding_stock = sanding_room.get_stock_by_sku(sku)
        sanding_qty = sanding_stock.quantity if sanding_stock else 0

        if sanding_qty < it.restock_point:
            wit = MountingWorkItem(sku, it.product.title)
            result.append(wit)

    return result


def sawing_work():
    """
    The saw room list tells the sawyer what icons need to be made so he can cut the boards needed to mount the icon prints onto.
    The criterion for inclusion in this list is that the sanding room stock level is less than the restock point.
    The “Need” column (see the attachment) is calculated by this formula: Need = full amount - sanding room stock.
    This list is sorted by “Need” (descending), and then by SKU (ascending).
    The Print Supply column in just the count of Icon Prints for sku in Wrapping Room
    """
    sanding_room = Room.objects.get(name__icontains="sand")
    wrapping_room = Room.objects.get(name__icontains="wrapping")
    mounted_icons = ProductInventory.objects.filter(
        product_type__name="mounted icon"
    ).order_by("sku")

    result = []

    for it in mounted_icons:
        sanding_stock = sanding_room.get_stock_by_sku(it.sku)
        sanding_qty = sanding_stock.quantity if sanding_stock else 0
        print_supply = wrapping_room.get_print_supply_by_sku(it.sku)

        ps_qty = print_supply.quantity if print_supply else 0
        if sanding_qty < it.restock_point:
            wit = SawingWorkItem(
                it.sku,
                it.product.title,
                ps_qty,
                it.target_amount - sanding_qty,
            )
            result.append(wit)

    return result
