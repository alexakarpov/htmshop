from django.test import TestCase
from .models import (
    ProductInventory,
    Room,
    Stock,
    PrintingWorkItem,
    SandingWorkItem,
)
from ecommerce.apps.inventory.utils import (
    padd,
    move_stock,
    sanding_work
)

from django.test import TestCase


class InventoryTest(TestCase):
    fixtures = [
        "catalogue.json",
        "inventory.json",
    ]

    UB_SKU = "a00100"
    BRIDEGROOM_SKU = "a00333"

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
        r = Room.objects.get(pk=3)  # Painting
        s = r.get_stock_by_sku("a00100")

        self.assertEqual(
            s.quantity, 1, "Painting room should have 1 of Unburning Bush"
        )

    def test_move_existing_sku(self):
        from_room = Room.objects.get(name__icontains="painting")
        to_room = Room.objects.get(name__icontains="Mounting")
        from_stock = from_room.get_stock_by_sku("a00100")
        to_stock = to_room.get_stock_by_sku("a00100")
        self.assertEqual(
            from_stock.quantity, 1, "Should start with 1 in Painting"
        )
        self.assertEqual(
            to_stock.quantity, 1, "Should start with 1 in Mounting"
        )
        to_stock = move_stock(from_stock, to_room, 1)

        self.assertEqual(
            from_stock.quantity, 0, "Should now be 0 in Painting"
        )
        self.assertEqual(to_stock.quantity, 2, "Should now be 2 in Mounting")

    def test_move_new_sku(self):
        from_room = Room.objects.get(name__icontains="Painting")
        to_room = Room.objects.get(name__icontains="Mounting")
        from_stock = from_room.get_stock_by_sku(self.BRIDEGROOM_SKU)
        to_stock = to_room.get_stock_by_sku(self.BRIDEGROOM_SKU)
        self.assertEqual(
            to_stock, None, "should be None for non-existing stock"
        )
        move_stock(from_stock, to_room, 1)
        to_stock = to_room.get_stock_by_sku(self.BRIDEGROOM_SKU)

        self.assertEqual(
            from_stock.quantity, 1, "Should now be 1 in Painting"
        )
        self.assertEqual(to_stock.quantity, 1, "Should now be 1 in Mounting")

    def test_move_to_empty_room(self):
        from_room = Room.objects.get(name__icontains="Painting")
        to_room = Room.objects.get(name__icontains="Sanding")
        from_stock = from_room.get_stock_by_sku(self.BRIDEGROOM_SKU)
        to_stock = to_room.get_stock_by_sku(self.BRIDEGROOM_SKU)

        self.assertEqual(
            to_stock, None, "should be None for non-existing stock"
        )
        move_stock(from_stock, to_room, 1)
        to_stock = to_room.get_stock_by_sku(self.BRIDEGROOM_SKU)

        self.assertEqual(
            from_stock.quantity, 1, "Should now be 1 in Painting"
        )
        self.assertEqual(to_stock.quantity, 1, "Should now be 1 in Mounting")

    def test_work_items(self):
        proom = Room.objects.get(name__icontains="Painting")
        wroom = Room.objects.get(name__icontains="wrapping")
        # painting has 1 of a00100 (BB) and 2 a00333 (Bridegroom) and no records fpr St Ephraim
        # wrapping has 2 of bridegroom, 3 of BB and 1 of St Ephraim

        # 

        work = sanding_work()
        self.assertEqual(len(work), 3)


