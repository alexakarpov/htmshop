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
            pk="a788a0d2-e54a-4d87-b652-1a0eda98a2a1")
        j_dict = json.loads(address.toJSON())
        acc = Account.objects.get(email='alexandre.karpov@protonmail.com')
        self.assertEquals(address.customer, acc)
        self.assertEquals(j_dict["full_name"], "Foo Bar",
                          "wrong name on the address")
        self.assertEquals(j_dict["city_locality"], "Seattle")
