import json

from django.test import TestCase

from .models import Order, OrderItem


class OrdersTest(TestCase):
    fixtures = ['accounts.json', ]

    def test_order_from_dicts(self):
        address_dict = ''
        basket_dict = ''

        self.assertEquals(2+2,5)
