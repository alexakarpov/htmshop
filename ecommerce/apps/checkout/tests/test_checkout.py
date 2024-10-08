from django.test import TestCase
from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.checkout.views import classify_order_add_items

class CheckoutTest(TestCase):
    fixtures = [
        "catalogue.json",
        "test_inventory.json"
    ]

    def test_item_set(self):
        assert(False)
