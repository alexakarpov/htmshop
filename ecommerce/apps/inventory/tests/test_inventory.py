from django.test import TestCase

from ecommerce.apps.inventory.models import (
    # ProductInventory,
    Room,
    # Stock,
    # PrintingWorkItem,
    # SandingWorkItem,
)
from ecommerce.apps.inventory.utils import padd, move_stock

from ecommerce.apps.inventory.lists import sanding_work

from django.test import TestCase


class InventoryTest(TestCase):
    fixtures = [
        "catalogue.json",
        "test_inventory.json",
    ]


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
        self.assertIsNone(t_stock, "wrapping starts with no A-9")

        moved_stock = move_stock(f_room, t_room, sku, qty=1)

        self.assertEqual(moved_stock.productinv.sku, f_stock.productinv.sku)
        f_stock.refresh_from_db()
        self.assertEqual(
            f_stock.quantity, 1, "from_stock after move qty decreased by 1"
        )
        self.assertEqual(
            moved_stock.quantity,
            1,
            "to_stock (moved stock) qty increased by 1",
        )

    def test_move_to_new(self):
        sku = "A-9"
        f_room = Room.objects.get(name__icontains="Paint")
        t_room = Room.objects.get(name__icontains="wrap")
        f_stock = f_room.get_stock_by_sku(sku)
        t_stock = t_room.get_stock_by_sku(sku)

        self.assertEqual(
            f_stock.quantity, 2, "painting starts with 2 of A-9"
        )
        self.assertEqual(
            t_stock, None, "A-9 should be missing from the wrapping room"
        )
        self.assertIsNone(
            t_stock, "that SKU should be missing from to_room altogether"
        )
        moved_stock = move_stock(f_room, t_room, sku, qty=1)

        self.assertEqual(moved_stock.productinv.sku, f_stock.productinv.sku)
        f_stock.refresh_from_db()
        self.assertEqual(
            f_stock.quantity, 1, "from_stock after move qty decreased by 1"
        )
        self.assertEqual(
            moved_stock.quantity,
            1,
            "new (moved) stock qty is 1",
        )

    def test_move_to_nowhere(self):
        sku = "A-9"
        f_room = Room.objects.get(name__icontains="paint")
        f_stock = f_room.get_stock_by_sku(sku)

        self.assertEqual(
            f_stock.quantity, 2, "painting starts with 2xA-9"
        )

        moved_stock = move_stock(f_room, None, sku, qty=1)
        f_stock.refresh_from_db()
        self.assertEqual(
            f_stock.quantity, 1, "from_stock after move qty decreased by 1"
        )
        self.assertIsNone(moved_stock)

    def test_move_from_nowhere(self):
        sku = "A-329"
        t_room = Room.objects.get(name__icontains="paint")
        self.assertIsNone(t_room.get_stock_by_sku(sku))

        moved_stock = move_stock(None, t_room, sku, qty=2)

        self.assertEqual(
            moved_stock.quantity, 2, "new stock created with qty of 3"
        )

        moved_stock = move_stock(None, t_room, sku, qty=2)

        self.assertEqual(
            moved_stock.quantity, 4, "new stock bumped to 4"
        )
