from django.test import TestCase
from ecommerce.apps.inventory.models import (
    # ProductInventory,
    Room,
    Stock,
    # PrintingWorkItem,
    # SandingWorkItem,
)
from ecommerce.apps.inventory.utils import (
    padd,
    move_stock,
    clean_room
)

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

    def test_get_stock_by_sku(self):
        r = Room.objects.get(name__icontains="Paint")
        s = r.get_stock_by_sku(UNBURNING_BUSH_SKU)

        self.assertEqual(
            s.quantity, 1, "Painting room should have 1 of Unburning Bush"
        )

    def test_move_existing_sku(self):
        from_room = Room.objects.get(name__icontains="painting")
        to_room = Room.objects.get(name__icontains="wrap")
        from_stock = from_room.get_stock_by_sku(UNBURNING_BUSH_SKU)
        to_stock = to_room.get_stock_by_sku(UNBURNING_BUSH_SKU)
        self.assertEqual(
            from_stock.quantity, 1, "Should start with 1 in Painting"
        )
        self.assertEqual(
            to_stock.quantity, 1, "Should start with 1 in wrapping"
        )
        to_stock = move_stock(from_stock, to_room, 1)

        self.assertEqual(
            from_stock.quantity, 0, "Should now be 0 in Painting"
        )
        self.assertEqual(to_stock.quantity, 2, "Should now be 2 in wrapping")

    # def test_move_new_sku(self):
    #     from_room = Room.objects.get(name__icontains="Painting")
    #     to_room = Room.objects.get(name__icontains="wrap")
    #     from_stock = from_room.stock_set.first()
    #     assert from_stock
    #     k=to_room.kill_sku(from_stock.product.sku)

    #     to_stock = to_room.get_stock_by_sku(BRIDEGROOM_SKU)
    #     self.assertEqual(
    #         to_stock, None, "should be None for non-existing stock"
    #     )
    #     move_stock(from_stock, to_room, 1)
    #     to_stock = to_room.get_stock_by_sku(self.BRIDEGROOM_SKU)

    #     self.assertEqual(
    #         from_stock.quantity, 1, "Should now be 1 in Painting"
    #     )
    #     self.assertEqual(to_stock.quantity, 1, "Should now be 1 in wrapping")

    # def test_move_to_empty_room(self):
    #     from_room = Room.objects.get(name__icontains="Painting")
    #     to_room = Room.objects.get(name__icontains="Sanding")
    #     from_stock = from_room.get_stock_by_sku(self.BRIDEGROOM_SKU)
    #     to_stock = to_room.get_stock_by_sku(self.BRIDEGROOM_SKU)

    #     self.assertEqual(
    #         to_stock, None, "should be None for non-existing stock"
    #     )
    #     move_stock(from_stock, to_room, 1)
    #     to_stock = to_room.get_stock_by_sku(self.BRIDEGROOM_SKU)

    #     self.assertEqual(
    #         from_stock.quantity, 1, "Should now be 1 in Painting"
    #     )
    #     self.assertEqual(to_stock.quantity, 1, "Should now be 1 in Mounting")
