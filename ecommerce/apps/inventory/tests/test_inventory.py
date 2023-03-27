from django.test import TestCase

from ecommerce.apps.inventory.models import (
    ProductInventory,
    Stock,
    get_stock_by_sku
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

    def test_move_between(self):
        sku = "A-9"
        f_room = "Paint"
        t_room = "sand"
        stock = get_stock_by_sku(sku)
        print(stock)
        self.assertEqual(
            stock.painting_qty, 2, "painting starts with 2 of A-9"
        )
        self.assertEqual(
            stock.sanding_qty, 0, "A-9 should be missing from the sanding room"
        )
        
        move_stock(f_room, t_room, sku, qty=1)

        stock.refresh_from_db()
        self.assertEqual(
            stock.painting_qty, 1, "painting stock after move qty decreased by 1"
        )
        self.assertEqual(
            stock.sanding_qty,
            1,
            "sanding qty is now 1",
        )

    def test_move_to_nowhere(self):
        sku = "A-9"
        stock = get_stock_by_sku(sku)

        self.assertEqual(
            stock.painting_qty, 2, "painting starts with 2xA-9"
        )

        stock = move_stock("painting", None, sku, 1)

        stock.refresh_from_db()
        self.assertEqual(
            stock.painting_qty, 1, " painting stock after move decreased by 1"
        )

    def test_move_from_nowhere(self):
        sku = "A-329"

        stock = get_stock_by_sku(sku)
        self.assertIsNotNone(stock, "stock gotta exist")
        # prepare
        stock.painting_qty = 0
        stock.save()
        #  confirm
        self.assertEqual(stock.painting_qty, 0, "starts with 0 in painting")

        stock = move_stock(None, "painting", sku, 2)

        stock.refresh_from_db()
        self.assertEqual(
            stock.painting_qty, 2, "stock now has 2 in painting")

        moved_stock = move_stock(None, "painting", sku, 2)

        stock.refresh_from_db()
        self.assertEqual(
            stock.painting_qty, 4, "new stock bumped to 4"
        )

    def test_move_new_from_nowhere(self):
        sku = "A-99"

        stock = get_stock_by_sku(sku)
        self.assertIsNone(stock, "stock doesnt exist")
        
        stock = move_stock(None, "painting", sku, 2)
        print(stock)

        stock.refresh_from_db()
        self.assertEqual(
            stock.painting_qty, 2, "stock now has 2 in painting")

        move_stock(None, "painting", sku, 2)
        stock.refresh_from_db()
        self.assertEqual(
            stock.painting_qty, 4, "new stock bumped to 4"
        )
