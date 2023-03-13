from django.test import TestCase

from ecommerce.apps.inventory.models import (
    # ProductInventory,
    Room,
    # PrintingWorkItem,
    # SandingWorkItem,
)
from ecommerce.apps.inventory.utils import padd, move_stock

from ecommerce.apps.inventory.lists import sanding_work
from .constants import UNBURNING_BUSH_SKU, BRIDEGROOM_SKU

from django.test import TestCase


class InventoryTest(TestCase):
    fixtures = [
        "catalogue.json",
        "test_inventory.json",
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

    def test_move_between_existing(self):
        sku = "A-9"
        f_room = Room.objects.get(name__icontains="Paint")
        t_room = Room.objects.get(name__icontains="wrap")

        f_stock = f_room.get_stock_by_sku(sku)
        t_stock = t_room.get_stock_by_sku(sku)

        self.assertEqual(f_stock.quantity, 2, "painting starts with 2 of A-9")
        self.assertEqual(t_stock.quantity, 1, "wrapping starts with 1 of A-9")

        moved_stock = move_stock(f_room, t_room, sku, qty=1)

        self.assertEqual(moved_stock.productinv.sku, f_stock.productinv.sku)
        f_stock.refresh_from_db()
        self.assertEqual(
            f_stock.quantity, 1, "from_stock after move qty decreased by 1"
        )
        self.assertEqual(
            moved_stock.quantity,
            2,
            "to_stock (moved stock) qty increased by 1",
        )

    def test_move_to_new(self):
        sku = "A-329"
        f_room = Room.objects.get(name__icontains="Paint")
        t_room = Room.objects.get(name__icontains="wrap")
        f_stock = f_room.get_stock_by_sku(sku)
        t_stock = t_room.get_stock_by_sku(sku)

        self.assertEqual(
            f_stock.quantity, 1, "painting starts with 1 of A-329"
        )
        self.assertEqual(
            t_stock, None, "A-329 should be missing from the target room"
        )
        self.assertIsNone(
            t_stock, "that SKU should be missing from to_room altogether"
        )
        moved_stock = move_stock(f_room, t_room, sku, qty=1)

        self.assertEqual(moved_stock.productinv.sku, f_stock.productinv.sku)
        f_stock.refresh_from_db()
        self.assertEqual(
            f_stock.quantity, 0, "from_stock after move qty decreased by 1"
        )
        self.assertEqual(
            moved_stock.quantity,
            1,
            "new (moved) stock qty is 1",
        )

    def test_move_to_nowhere(self):
        sku = "A-329"
        f_room = Room.objects.get(name__icontains="Paint")
        f_stock = f_room.get_stock_by_sku(sku)

        self.assertEqual(
            f_stock.quantity, 1, "painting starts with 1 of A-329"
        )

        moved_stock = move_stock(f_room, None, sku, qty=1)
        f_stock.refresh_from_db()
        self.assertEqual(
            f_stock.quantity, 0, "from_stock after move qty decreased by 1"
        )
        self.assertIsNone(moved_stock)

    def test_move_from_nowhere(self):
        sku = "A-329"
        t_room = Room.objects.get(name__icontains="paint")

        moved_stock = move_stock(None, t_room, sku, qty=3)

        self.assertEqual(
            moved_stock.quantity, 3, "new stock created with qty of 3"
        )
