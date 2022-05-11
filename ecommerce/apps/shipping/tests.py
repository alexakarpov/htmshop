import unittest

from django.test import TestCase
from ecommerce.apps.accounts.models import Address

from .engine import make_shipment
from .utils import get_weight

# # Create your tests here.
# def test_get_weight():
#     basket = {
#         "basket": {
#             "2": {"price": "30.00", "qty": 1, "variant": "8x10", "title": "Holy Napkin", "weight": 16},
#             "1": {"price": "20.00", "qty": 2, "variant": "", "title": "Prayer Book", "weight": 8},
#         }
#     }
#     assert get_weight(basket) == 32


def test_make_shipment():
    b = {}
    a = Address()
    a.full_name = "John Doe"
    a.address_line = "1 Main St"
    a.postcode = "98765"

    s = make_shipment(b, a)
    sd = s["shipment"]
    assert "usps_parcel_select" in s["rate_options"]["service_codes"]
    assert sd["ship_from"]["company_name"] == "Holy Transfiguration Monastery"
    assert sd["ship_to"]["postal_code"] == a.postcode
    assert sd["ship_to"]["country_code"] == a.country == "US"
    assert sd.get("packages") == []
