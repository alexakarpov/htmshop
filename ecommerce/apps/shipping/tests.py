import imp
import json
import unittest

from django.test import TestCase
from ecommerce.apps.accounts.models import Address

from .choice import ShippingChoice, rate_to_choice, split_tiers
from .engine import make_shipment
from .serializers import ShippingChoiceSerializer
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


def test_tiers():
    r1 = {
        "rate_id": "se-123",
        "shipping_amount": {"amount": 17.74},
        "delivery_days": 5,
        "service_code": "fedex_standard_overnight", # expedite
    }
    r2 = {
        "rate_id": "se-231",
        "shipping_amount": {"amount": 27.29},
        "delivery_days": 3,
        "service_code": "usps_priority_mail", # regular
    }
    r3 = {
        "rate_id": "se-145",
        "shipping_amount": {"amount": 37.29},
        "delivery_days": 1,
        "service_code": "fedex_2day", # fast
    }

    choices = list(map(lambda r: rate_to_choice(r), [r1,r2,r3]))
    tiers = split_tiers(choices)
    assert choices[0].price == 17.74
    assert choices[0].name == "fedex_standard_overnight"
    assert tiers["regular"][0].name == "usps_priority_mail"
    assert tiers["fast"][0].name == "fedex_2day"
    assert tiers["express"][0].name == "fedex_standard_overnight"


def test_shipping_choice_seriaizer():
    c = ShippingChoice("nameo", 21.99, "qwe123", 9)
    ser = ShippingChoiceSerializer(c)
    assert ser.data.get("name") == "nameo"
    assert ser.data.get("price") == 21.99
    assert ser.data.get("id") == "qwe123"
    assert ser.data.get("days") == 9
