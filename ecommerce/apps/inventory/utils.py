import logging

from .models import ProductInventory
from ecommerce.constants import MOUNTED_ICON_TYPE_NAME, ICON_PRINT_TYPE_NAME, WS_SEPARATOR

logger=logging.getLogger("console")

def mounted_icons(inventory):
    return list(filter(lambda x: x.product_type.name == MOUNTED_ICON_TYPE_NAME, inventory))

def prints(inventory):
    return list(filter(lambda x: x.product_type.name == ICON_PRINT_TYPE_NAME, inventory))

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


def print_work(inventory):
    prints_inventory = prints(inventory)
    result = []
    
    longest=0
    for it in prints_inventory:
        s = it.sku
        if len(s) > longest:
            longest = len(s)
    logger.debug(f"LONGEST SKU is {longest} chars")
    result.append(header(longest))
    
    for it in prints_inventory:
        if it.quantity < it.restock_point:
            w_qty = it.target_amount - it.quantity
            padded, l = padd(it.sku, longest)
            result.append( f"{padded} {WS_SEPARATOR[0:l-longest]} {WS_SEPARATOR} - {w_qty} - {WS_SEPARATOR} __")
        else:
            continue
    
    return result
 
def mount_work(inventory):
    return mounted_icons(inventory)
