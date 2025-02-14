from django.test import TestCase

from ecommerce.apps.orders.models import Order

class InventoryTest(TestCase):
    fixtures = [
        "test_orders.json",
        "test_inventory.json",
        "test_accounts.json",
        "test_catalogue.json",
    ]

    def test_get_address_json(self):
        o1 = Order.objects.first()
        aj = o1.address_json()
        oj = o1.to_dict()
        print(dir(oj))
        self.assertEqual(aj, oj)
