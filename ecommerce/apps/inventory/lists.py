import logging

from ecommerce.apps.inventory.models import (
    MountingWorkItem,
    PrintingWorkItem,
    Stock,
    SandingWorkItem,
    SawingWorkItem,
    get_or_create_stock_by_sku,
    get_print_supply_by_sku,
)

logger = logging.getLogger("django")


def print_work():
    inventory = Stock.objects.filter(sku__iendswith="P")

    result = []
    for it in inventory:
        if it.wrapping_qty < it.restock_point:
            w_qty = it.target_amount - it.wrapping_qty
            wit = PrintingWorkItem(
                it.sku,
                it.product.title,
                w_qty,
            )
            result.append(wit)
        else:
            continue
    return result


def sanding_work():
    mounted_icons = Stock.objects.filter(product_type__name="mounted icon").order_by("sku")

    result = []

    for it in mounted_icons:
        sku = it.sku
        stock = get_or_create_stock_by_sku(sku)

        w_qty = stock.wrapping_qty if stock else 0
        p_qty = stock.painting_qty if stock else 0
        s_qty = stock.sanding_qty if stock else 0

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
            logger.debug(f"above the restock point ({it.restock_point}), continuing")
            continue
    return sorted(result)


def mounting_work():
    mounted_icons = Stock.objects.filter(product_type__name="mounted icon").order_by("sku")
    result = []

    for it in mounted_icons:
        sku = it.sku
        stock = get_or_create_stock_by_sku(sku)
        sanding_qty = stock.sanding_qty if stock else 0

        if sanding_qty < it.restock_point:
            wit = MountingWorkItem(sku, it.product.title)
            result.append(wit)

    return sorted(result)


def sawing_work():
    """
    The saw room list tells the sawyer what icons need to be made so he can cut the boards needed to mount the icon prints onto.
    The criterion for inclusion in this list is that the sanding room stock level is less than the restock point.
    The “Need” column (see the attachment) is calculated by this formula: Need = full amount - sanding room stock.
    This list is sorted by “Need” (descending), and then by SKU (ascending).
    The Print Supply column in just the count of Icon Prints for sku in Wrapping Room
    """
    mounted_icons = Stock.objects.filter(product_type__name="mounted icon")

    result = []

    for it in mounted_icons:
        stock = get_or_create_stock_by_sku(it.sku)
        sanding_qty = stock.sanding_qty if stock else 0
        print_supply = get_print_supply_by_sku(it.sku)

        ps_qty = print_supply.wrapping_qty if print_supply else 0
        if sanding_qty < it.restock_point:
            wit = SawingWorkItem(
                it.sku,
                it.product.title,
                ps_qty,
                it.target_amount - sanding_qty,
            )
            result.append(wit)

    return sorted(result)
