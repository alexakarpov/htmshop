import imp
import json
import unittest

from django.test import TestCase
from ecommerce.apps.accounts.models import Address

from .choice import rate_to_choice
from .engine import make_shipment
from .utils import get_weight


def test_make_shipment():
    b = [
        {"price": "30.00", "qty": 1, "variant": "8x10", "title": "Holy Napkin", "weight": 16},
        {"price": "20.00", "qty": 1, "variant": "", "title": "Prayer Book", "weight": 8},
    ]
    a = Address()
    a.full_name = "John Doe"
    a.address_line = "1 Main St"
    a.postcode = "98765"

    s = make_shipment(b, a)
    sd = s["shipment"]
    assert sd["ship_from"]["company_name"] == "Holy Transfiguration Monastery"
    assert sd["ship_to"]["postal_code"] == a.postcode
    assert sd["ship_to"]["country_code"] == a.country == "US"
    assert sd.get("packages") == [{"weight": {"value": 24, "unit": "ounce"}}]


def test_rate_to_choice():
    with open("shipping_jsons/rate.json", "r") as f:
        rate = json.load(f)
        choice = rate_to_choice(rate)
        assert choice.price == 17.74
        assert choice.name == "usps_priority_mail"
