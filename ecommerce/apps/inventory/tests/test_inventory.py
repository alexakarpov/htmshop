from django.test import TestCase

from ..models import (
    get_or_create_stock_by_sku
)
# from ecommerce.apps.inventory.utils import move_stock
from ..utils import move_stock_one_sku, move_sku_to_print_supply, move_sku_from_print_supply
from ecommerce.apps.inventory.lists import sanding_work

from django.test import TestCase


class InventoryTest(TestCase):
    fixtures = [
        "catalogue.json",
        "test_inventory.json"
    ]


    def test_move_between(self):
        sku = "A-9"

        stock = get_or_create_stock_by_sku(sku)
        print(f"testing {stock}")
        self.assertEqual(
            stock.painting_qty, 2, "painting starts with 2 of A-9"
        )
        self.assertEqual(
            stock.sanding_qty, 0, "A-9 should be missing from the sanding room"
        )

        stock = move_stock_one_sku(
            sku, from_room="painting", to_room="sanding", qty=1)

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
        stock = get_or_create_stock_by_sku(sku)

        self.assertEqual(
            stock.painting_qty, 2, "painting starts with 2xA-9"
        )

        stock = move_stock_one_sku(sku, from_room="painting", qty=1)

        self.assertEqual(
            stock.painting_qty, 1, " painting stock after move decreased by 1"
        )

    def test_move_from_nowhere(self):
        sku = "A-329"

        stock = get_or_create_stock_by_sku(sku)
        self.assertIsNotNone(stock, "stock gotta exist")

        #  confirm
        self.assertEqual(stock.painting_qty, 0, "starts with 0 in painting")

        stock = move_stock_one_sku(sku, to_room="painting", qty=2)

        self.assertEqual(
            stock.painting_qty, 2, "stock now has 2 in painting")

        moved_stock = move_stock_one_sku(sku, to_room="painting", qty=3)

        self.assertEqual(
            moved_stock.painting_qty, 5, "stock bumped to 5"
        )

    def test_move_new_from_nowhere(self):
        sku = "A-122"  # there is no stock for this sku, but ProductInventory exists

        stock = move_stock_one_sku(sku, to_room="painting", qty=2)
        self.assertIsNotNone(stock)
        stock.refresh_from_db()
        self.assertEqual(
            stock.painting_qty, 2, "stock now has 2 in painting")

        move_stock_one_sku(sku, to_room="painting", qty=2)
        stock.refresh_from_db()
        self.assertEqual(
            stock.painting_qty, 4, "new stock bumped to 4"
        )

    def test_move_to_print_supply(self):
        sku = "A-9"
        p_sku = "A-9P"

        stock = get_or_create_stock_by_sku(p_sku)
        self.assertEqual(stock.wrapping_qty, 7,
                         "should start with 7 prints in wrapping")
        stock = move_sku_to_print_supply(sku, from_room="nowhere", qty=2)
        stock.refresh_from_db()
        self.assertEqual(stock.wrapping_qty, 2+7, "should be 7+2 after move")

        self.assertEqual(stock.sku, "A-9P")

    def test_move_from_print_supply(self):
        """
        remember, print supply is really the wrapping room filtered down to just prints
        moving from PS to any other room will drop print sku wrapping qty and bump the mounted sku
        """
        sku = "A-9"
        p_sku = "A-9P"

        p_stock = get_or_create_stock_by_sku(p_sku)
        m_stock = get_or_create_stock_by_sku(sku)

        self.assertEqual(p_stock.wrapping_qty, 7,
                         "starts with 7 of A-9P in Print Supply/wrapping")
        self.assertEqual(m_stock.wrapping_qty, 5,
                         "starts with 5 of A-9 in wrapping")

        m_stock = move_sku_from_print_supply(sku,
                                             to_room="wrapping",
                                             qty=3)
        # this must become a stock of mounted icons in the wrapping room
        m_stock.refresh_from_db()
        p_stock.refresh_from_db()

        self.assertEqual(m_stock.wrapping_qty, 5+3,
                         "should bump A-9 in wrapping to 8")
        self.assertEqual(p_stock.wrapping_qty, 7-3,
                         "should drop A-9P in print supply by 3")
