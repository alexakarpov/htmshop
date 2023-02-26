import json

from django.test import TestCase

from .models import Order, OrderItem, make_order


class OrdersTest(TestCase):
    fixtures = [
        "accounts.json",
    ]

    def test_order_from_dicts(self):
        test_cart_d = {
            "skuxx": {
                "price": "30.00",
                "qty": 2,
                "variant": "8x10",
                "title": "Holy Napkin",
                "weight": 16,
            },
            "skuyy": {
                "price": "20.00",
                "qty": 1,
                "title": "Prayer Book",
                "weight": 8,
            },
        }

        test_address_d = {
            "full_name": "Testy Testo",
            "address_line1": "1 qwe st",
            "address_line2": "",
            "phone": "1231231234",
            "city_locality": "Qwepolis",
            "state_province": "SC",
            "postal_code": "1231234",
            "country_code": "US",
        }

        order = make_order(
            test_address_d, test_cart_d, "testytesto@example.com"
        )

        order.save()

        self.assertEqual(order.full_name, "Testy Testo")
        self.assertEqual(order.email, "testytesto@example.com")
        self.assertEqual(order.total_paid, 2 * 30 + 20)
