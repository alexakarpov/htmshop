from django.test import TestCase
from ecommerce.apps.inventory.models import (
    # ProductInventory,
    Room,
    Stock,
    # PrintingWorkItem,
    # SandingWorkItem,
)
from ecommerce.apps.inventory.utils import padd, move_stock, clean_room

from ecommerce.apps.inventory.lists import sanding_work
from .constants import UNBURNING_BUSH_SKU, BRIDEGROOM_SKU

from django.test import TestCase


class InventoryTest(TestCase):
    fixtures = [
        "catalogue.json",
        "inventory.json",
    ]

    BRIDEGROOM_SKU = "a-03"

    def test_padding(self):
        px = padd("abc", 5)
        self.assertEqual(px, ("abc  ", 2))
        px = padd("abcd", 4)
        self.assertEqual(px, ("abcd", 0))
        px = padd("abcd", 3)
        self.assertEqual(px, ("abcd", 0))
        px = padd("-", 10, c="-")
        self.assertEqual(px, ("-" * 10, 9))

    def test_move_to_existing(self):
        f_room = Room.objects.get(name__icontains="Paint")
        t_room = Room.objects.get(name__icontains="wrap")
        f_stock = f_room.get_stock_by_sku("A-9")
        t_stock = t_room.get_stock_by_sku("A-9")

        self.assertEqual(f_stock.quantity, 2, "painting starts with 2 of A-9")
        self.assertEqual(t_stock.quantity, 1, "wrapping starts with 1 of A-9")

        moved_stock = f_stock.move_to_room(t_room, 1)

        self.assertEqual(moved_stock, t_stock, "should be the same stock")

        self.assertEqual(moved_stock.product.sku, f_stock.product.sku)
        self.assertEqual(
            f_stock.quantity, 1, "from_stock after move qty decreased by 1"
        )
        self.assertEqual(
            moved_stock.quantity,
            2,
            "to_stock (moved stock) qty increased by 1",
        )

    def test_move_to_new(self):
        f_room = Room.objects.get(name__icontains="Paint")
        t_room = Room.objects.get(name__icontains="wrap")
        f_stock = f_room.get_stock_by_sku("A-329")
        t_stock = t_room.get_stock_by_sku("A-329")

        self.assertEqual(
            f_stock.quantity, 1, "painting starts with 1 of A-329"
        )
        self.assertEqual(
            t_stock, None, "A-329 should be missing from the target room"
        )

        moved_stock = f_stock.move_to_room(t_room, 1)

        self.assertEqual(moved_stock.product.sku, f_stock.product.sku)
        self.assertEqual(
            f_stock.quantity, 0, "from_stock after move qty decreased by 1"
        )
        self.assertEqual(
            moved_stock.quantity,
            1,
            "new (moved) stock qty is 1",
        )
