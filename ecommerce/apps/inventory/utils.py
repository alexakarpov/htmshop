import logging

from ecommerce.apps.inventory.models import (
    ProductStock,
    get_or_create_stock_by_sku,
)
from ecommerce.constants import (
    MOUNTED_ICON_TYPE_NAME,
    ICON_PRINT_TYPE_NAME,
)

logger = logging.getLogger("django")


def move_stock_one_sku(sku: str, from_room: str = 'nowhere', to_room: str = 'nowhere',  qty: int = 1) -> ProductStock:
    """
    move stock between rooms, including to/from nowhere
    the normal case is when only one stock is involved

    if to_room is print supply, we have two stock objects to adjust:
        from_stock (SKU) qty only decreases
        to_stock, (print SKU) only increases
    likewise, if from_room is print supply:
        from_stock (print SKU) qty only decreases
        to_stock, (SKU) only increases
    , and in both cases two stock objects are affected,

    otherwise, only one stock object is affected

    """
    assert from_room != "nowhere" or to_room != "nowhere", "at least one room must be provided"

    to_room = to_room.lower()
    from_room = from_room.lower()

    logger.debug(
        f"moving {sku}x{qty} from {from_room} to {to_room}")

    stock = get_or_create_stock_by_sku(sku)

    stock.settle_quantities(qty, from_room, to_room)

    stock.save()
    logger.debug(f"move finished, returning {stock}")
    return stock


def move_sku_to_print_supply(source_sku: str, from_room: str, qty: int = 1) -> ProductStock:
    print_sku = source_sku+"P"

    stock = get_or_create_stock_by_sku(print_sku)
    logger.info(f"stock is {stock}")
    stock.wrapping_qty += qty
    stock.save()
    return stock


def move_sku_from_print_supply(sku: str, to_room: str,  qty: int = 1) -> ProductStock:
    print_sku = sku+"P"

    print_stock = get_or_create_stock_by_sku(print_sku)
    print_stock.wrapping_qty -= qty  # print supply IS prints in wrapping room
    print_stock.save()
    to_stock = get_or_create_stock_by_sku(sku)
    to_stock.settle_quantities(qty, "print supply", to_room)
    to_stock.save()
    return to_stock
