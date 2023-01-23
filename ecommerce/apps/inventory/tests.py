from django.test import TestCase
from ecommerce.apps.inventory.models import ProductInventory
from ecommerce.apps.inventory.utils import print_work, mount_work, padd

from django.test import TestCase


class InventoryTest(TestCase):
    fixtures = [
        "catalogue.json",
        "inventory.json",
    ]

    def test_mounted_icons(self):
        test_inventory = ProductInventory.objects.all()
        self.assertEquals(len(test_inventory), 9)
        work = mount_work   (test_inventory)
        self.assertEquals(len(work), 3)

    # def test_print_work(self):
    #     test_inventory = ProductInventory.objects.all()
    #     [work] = print_work(test_inventory)
    #     self.assertEquals(len(work.split(',')), 2)

    def test_padding(self):
        px=padd('abc', 5)
        self.assertEquals(px, ('abc  ', 2))
        px=padd('abcd', 4)
        self.assertEquals(px, ('abcd', 0))
        px=padd('abcd', 3)
        self.assertEquals(px, ('abcd', 0))
        px = padd('-', 10, c='-')
        self.assertEquals(px, ('-'*10,9))