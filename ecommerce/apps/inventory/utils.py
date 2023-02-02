import logging

from .models import ProductInventory, WorkItem
from ecommerce.constants import MOUNTED_ICON_TYPE_NAME, ICON_PRINT_TYPE_NAME, WS_SEPARATOR

logger=logging.getLogger("console")

def filter_inventory(inventory, kind):
    return list(filter(lambda x: x.product_type.name == kind, inventory))

def padd(it, l, c=' '):
    if len(it) >= l:
        logger.debug(f"{it} is >= of {l}, not padding")
        return (it, 0)

    else:
        p = l-len(it)
        logger.debug(f"{it} needs padding of {p}")
        return (it + (c * p), p)

def header(l):
    (paddedx, lth) = padd('-', l, c='-')
    logger.debug(f"paddedx= {paddedx}, lth is {lth}")
    return f"SKU" + paddedx + "|QTY|" + "^^^" * 4 + "|PRINTED|^^^"

def print_work(inventory=ProductInventory.objects.all()):
    inv = filter_inventory(inventory, ICON_PRINT_TYPE_NAME)
    result = []
    for it in inv:
        if it.quantity < it.restock_point:
            w_qty = it.target_amount - it.quantity
            result.append(WorkItem(it.sku, it.product.title, it.product_type.name, w_qty) )
        else:
            continue
    return result

def mount_work(inventory):
    return filter_inventory(inventory, MOUNTED_ICON_TYPE_NAME)
