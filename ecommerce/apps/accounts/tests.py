import json

from django.test import TestCase

from .models import Account, Address


class AccountTest(TestCase):
    fixtures = ['accounts.json', ]

    def test_fixture_worked(self):
        self.assertEquals(Account.objects.all().count(),
                          3,
                          "fixture has 3 accounts")

    def test_address_from_json(self):
        address = Address.objects.get(
            pk='802596f0-1d01-4770-9a1c-bc453bcd6668')
        j_dict = json.loads(address.toJSON())
        acc = Account.objects.get(email='alexandre.karpov@protonmail.com')
        self.assertEquals(address.customer, acc)
        self.assertEquals(j_dict["full_name"], "John Doe",
                          "wrong name on the address")
        self.assertEquals(j_dict["city_locality"], "San Francisco")
