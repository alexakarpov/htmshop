from django.test import TestCase
from .models import ProductInventory, Room, Stock
from ecommerce.apps.inventory.utils import (
    print_work,
    mount_work,
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

    def test_mounted_icons(self):
        test_inventory = ProductInventory.objects.all()
        self.assertEquals(len(test_inventory), 12, "12 items in inventory")
        work = mount_work(test_inventory)
        self.assertEquals(len(work), 3)

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
        from_room = Room.objects.get(pk=3)  # Painting
        to_room = Room.objects.get(pk=2)  # Mounting
        from_stock = from_room.get_stock_by_sku("a00100")
        move_stock(from_stock, to_room, 1)
        to_stock = to_room.get_stock_by_sku("a00100")
        self.assertEquals(
            from_stock.quantity, 0, "Should now be 0 in Painting"
        )
        self.assertEquals(to_stock.quantity, 1, "Should now be 1 in Mounting")

    def test_move_new_sku(self):
        from_room = Room.objects.get(pk=3)  # Painting
        to_room = Room.objects.get(pk=2)  # Mounting

        from_stock = from_room.get_stock_by_sku(self.BRIDEGROOM_SKU)
        move_stock(from_stock, to_room, 1)
        to_stock = to_room.get_stock_by_sku(self.BRIDEGROOM_SKU)
        self.assertEquals(
            from_stock.quantity, 1, "Should now be 1 in Painting"
        )
        self.assertEquals(to_stock.quantity, 1, "Should now be 1 in Mounting")
