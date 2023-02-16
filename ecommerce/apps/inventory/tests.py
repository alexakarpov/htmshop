from django.test import TestCase
from .models import ProductInventory, Room, Stock
from ecommerce.apps.inventory.utils import (
    padd,
    move_stock,
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
        self.assertEquals(px, ("abc  ", 2))
        px = padd("abcd", 4)
        self.assertEquals(px, ("abcd", 0))
        px = padd("abcd", 3)
        self.assertEquals(px, ("abcd", 0))
        px = padd("-", 10, c="-")
        self.assertEquals(px, ("-" * 10, 9))

    def test_get_stock_by_sku(self):
        r = Room.objects.get(pk=3)  # Painting
        s = r.get_stock_by_sku("a00100")

        self.assertEquals(
            s.quantity, 1, "Painting room should have 1 of Unburning Bush"
        )

    def test_move_existing_sku(self):
        from_room = Room.objects.get(name__icontains='painting')
        to_room = Room.objects.get(name__icontains='Mounting')
        from_stock = from_room.get_stock_by_sku("a00100")
        to_stock=to_room.get_stock_by_sku("a00100")
        self.assertEquals(
            from_stock.quantity, 1, "Should start with 1 in Painting"
        )
        self.assertEquals(
            to_stock.quantity, 1, "Should start with 1 in Mounting"
        )
        to_stock = move_stock(from_stock, to_room, 1)
        
        self.assertEquals(
            from_stock.quantity, 0, "Should now be 0 in Painting"
        )
        self.assertEquals(to_stock.quantity, 2, "Should now be 2 in Mounting")

    def test_move_new_sku(self):
        from_room = Room.objects.get(name__icontains="Painting")
        to_room = Room.objects.get(name__icontains="Mounting")
        from_stock = from_room.get_stock_by_sku(self.BRIDEGROOM_SKU)
        to_stock = to_room.get_stock_by_sku(self.BRIDEGROOM_SKU)
        self.assertEquals(
            to_stock, None, "should be None for non-existing stock"
        )
        move_stock(from_stock, to_room, 1)
        to_stock = to_room.get_stock_by_sku(self.BRIDEGROOM_SKU)

        self.assertEquals(
            from_stock.quantity, 1, "Should now be 1 in Painting"
        )
        self.assertEquals(to_stock.quantity, 1, "Should now be 1 in Mounting")

    def test_move_to_empty_room(self):
        from_room = Room.objects.get(name__icontains="Painting")
        to_room = Room.objects.get(name__icontains="Sanding")
        from_stock = from_room.get_stock_by_sku(self.BRIDEGROOM_SKU)
        to_stock = to_room.get_stock_by_sku(self.BRIDEGROOM_SKU)

        self.assertEquals(
            to_stock, None, "should be None for non-existing stock"
        )
        move_stock(from_stock, to_room, 1)
        to_stock = to_room.get_stock_by_sku(self.BRIDEGROOM_SKU)

        self.assertEquals(
            from_stock.quantity, 1, "Should now be 1 in Painting"
        )
        self.assertEquals(to_stock.quantity, 1, "Should now be 1 in Mounting")
