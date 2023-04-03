import logging

from .models import (
    ProductStock,
    get_or_create_stock_by_sku,
)
from ecommerce.constants import (
    MOUNTED_ICON_TYPE_NAME,
    ICON_PRINT_TYPE_NAME,
)

logger = logging.getLogger("django")

# def padd(it, l, c=" "):
#     if len(it) >= l:
#         return (it, 0)
#     else:
#         p = l - len(it)
#         return (it + (c * p), p)


def move_stock(sku: str, from_room: str = 'nowhere', to_room: str = 'nowhere',  qty: int = 1) -> ProductStock:
    """
    move stocks between rooms, including to/from nowhere
    """
    assert from_room or to_room, "at least one room must be provided"
    
    to_room = to_room.lower()
    from_room = from_room.lower()

    logger.debug(
        f"moving {sku}x{qty} from {from_room} to {to_room}")

    stock = get_or_create_stock_by_sku(sku) # stock record may not even exist yet

    logger.debug(f"stock object is {stock}")

    if to_room.find("print") > -1:
        print_sku = sku+"P" # transform to print sku
        stock = get_or_create_stock_by_sku(print_sku)
        
    stock.settle_quantities(qty, from_room, to_room)

    stock.save()
    stock.refresh_from_db()
    return stock
