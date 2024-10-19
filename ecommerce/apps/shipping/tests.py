import json, os
from unittest.mock import patch

# Third-party imports...
from rest_framework.test import APIRequestFactory, APITestCase
from django.conf import settings

from ecommerce.apps.accounts.models import Address
from ecommerce.apps.basket.basket import get_weight
from ecommerce.apps.shipping.views import get_rates

from .choice import ShippingChoiceSE, rate_to_choice, split_tiers
from .engine import make_SE_shipment
from .serializers import ShippingChoiceSESerializer
from ecommerce.apps.shipping.engine import shipping_choices_SE

# import unittest

test_cart = {
    "TEST_SKU1": {
        "price": "30.00",
        "qty": 1,
        "variant": "8x10",
        "title": "Holy Napkin",
        "weight": 16,
    },
    "TEST_SKU2": {
        "price": "20.00",
        "qty": 1,
        "variant": "",
        "title": "Prayer Book",
        "weight": 8,
    },
}


test_address = Address()
test_address.full_name = "John Doe"
test_address.address_line1 = "1 Main St"
test_address.postal_code = "98765"
test_address.city_locality = "Boston"


class SimpleTest(APITestCase):
    fixtures = ["accounts.json"]

    @patch("ecommerce.apps.shipping.engine.shipengine.get_rates_from_shipment")
    def test_api(self, mock_get_rates_from_shipment):
        factory = APIRequestFactory()
        request = factory.get("/shipping/get-rates/")
        request.session = {}
        address = Address.objects.get(
            pk="b4f01be6-c9e5-442a-a67b-3f3a484502e4"
        )
        self.assertEqual(address.country_code, "US")
        aj = address.toJSON()
        request.session["address"] = aj
        cwd = os.getcwd()
        print("Current working directory:", cwd)
        with open("ecommerce/apps/shipping/data/grfsr.json", "r") as f:
            rates_response = json.load(f)
        mock_get_rates_from_shipment.return_value = rates_response

        view = get_rates
        self.assertEqual(Address.objects.count(), 2)
        response = view(request)
        choices_j = json.loads(response.content).get("choices")
        self.assertEqual(len(choices_j), 3)

    def test_make_shipment(self):
        s = make_SE_shipment(test_cart, test_address.to_dict())

        sd = s["shipment"]
        assert (
            sd["ship_from"]["company_name"] == "Holy Transfiguration Monastery"
        )
        self.assertEqual(
            sd["ship_to"]["postal_code"], test_address.postal_code
        )
        self.assertEqual(sd["ship_to"]["full_name"], test_address.full_name)
        self.assertEqual(
            sd["ship_to"]["country_code"], test_address.country_code
        )
        self.assertEqual(
            sd["ship_to"]["city_locality"], test_address.city_locality
        )
        self.assertEqual(
            sd.get("packages"),
            [{"weight": {"value": get_weight(test_cart), "unit": "ounce"}}],
        )

    def test_rate_to_choice(self):
        with open("shipping_jsons/rate.json", "r") as f:
            rate = json.load(f)
            choice = rate_to_choice(rate)
            assert choice.price == 17.74
            assert choice.service_code == "usps_priority_mail"

    def test_tiers(self):
        r1 = {
            "rate_id": "se-123",
            "shipping_amount": {"amount": 97.74},
            "delivery_days": 1,
            "service_code": "fedex_standard_overnight",  # expedite
        }
        r2 = {
            "rate_id": "se-231",
            "shipping_amount": {"amount": 7.29},
            "delivery_days": 5,
            "service_code": "usps_priority_mail",  # regular
        }
        r3 = {
            "rate_id": "se-145",
            "shipping_amount": {"amount": 47.29},
            "delivery_days": 2,
            "service_code": "fedex_2day",  # fast
        }
        choices = list(map(lambda r: rate_to_choice(r), [r1, r2, r3]))
        tiers = split_tiers(choices)

        assert tiers["fast"][0].service_code == "fedex_2day"
        assert tiers["express"][0].service_code == "fedex_standard_overnight"

# TODO: need a test for choices for baskets eligible for USPS First Class


    def test_tiers_intl(self):
        choices_str = [
            {
                "service_code": "ups_worldwide_express",
                "shipping_amount": {"amount": 116.56},
                "rate_id": "se - 5985783216",
                "delivery_days": 1,
            },
            {
                "service_code": "ups_worldwide_expedited",
                "shipping_amount": {"amount": 104.93},
                "rate_id": "se - 5985783217",
                "delivery_days": 2,
            },
            {
                "service_code": "ups_standard_international",
                "shipping_amount": {"amount": 25.41},
                "rate_id": "se - 5985783218",
                "delivery_days": 3,
            },
            {
                "service_code": "ups_worldwide_express_plus",
                "shipping_amount": {"amount": 116.56},
                "rate_id": "se - 5985783219",
                "delivery_days": 1,
            },
            {
                "service_code": "ups_worldwide_saver",
                "shipping_amount": {"amount": 112.07},
                "rate_id": "se - 5985783220",
                "delivery_days": 1,
            },
            {
                "service_code": "usps_first_class_mail_international",
                "shipping_amount": {"amount": 16.46},
                "rate_id": "se - 5985783221",
                "delivery_days": 2,
            },
            {
                "service_code": "usps_priority_mail_international",
                "shipping_amount": {"amount": 40.91},
                "rate_id": "se - 5985783222",
                "delivery_days": 10,
            },
            {
                "service_code": "usps_priority_mail_express_international",
                "shipping_amount": {"amount": 57.32},
                "rate_id": "se-5985783223",
                "delivery_days": 5,
            },
            {
                "service_code": "globalpost_economy",
                "shipping_amount": {"amount": 13.04},
                "rate_id": "se - 5985783224",
                "delivery_days": 14,
            },
            {
                "service_code": "globalpost_priority",
                "shipping_amount": {"amount": 12.69},
                "rate_id": "se - 5985783225",
                "delivery_days": 10,
            },
            {
                "service_code": "gp_plus",
                "shipping_amount": {"amount": 11.5},
                "rate_id": "se-5985783226",
                "delivery_days": 5,
            },
            {
                "service_code": "fedex_international_economy",
                "shipping_amount": {"amount": 106.69},
                "rate_id": "se-5985783227",
                "delivery_days": 1,
            },
            {
                "service_code": "fedex_ground_international",
                "shipping_amount": {"amount": 25.45},
                "rate_id": "se - 5985783228",
                "delivery_days": 3,
            },
            {
                "service_code": "fedex_international_priority_express",
                "shipping_amount": {"amount": 118.26},
                "rate_id": "se - 5985783229",
                "delivery_days": 1,
            },
            {
                "service_code": "fedex_international_connect_plus",
                "shipping_amount": {"amount": 98.69},
                "rate_id": "se-5985783230",
                "delivery_days": 1,
            },
            {
                "service_code": "fedex_international_priority",
                "shipping_amount": {"amount": 112.95},
                "rate_id": "se - 5985783231",
                "delivery_days": 1,
            },
        ]

        choices = list(map(lambda r: rate_to_choice(r), choices_str))
        tiers = split_tiers(choices, international=True)
        self.assertEqual(3, len(tiers.values()))

    def test_shipping_choice_serializer(self):
        c = ShippingChoiceSE(21.99, "some_fake_id", "fake_service_code", 3)
        ser = ShippingChoiceSESerializer(c)
        assert ser.data.get("price") == 21.99
        assert ser.data.get("service_code") == "fake_service_code"
        assert ser.data.get("days") == 3

    def test_funky(self):
        self.assertTrue(settings.HARDCODE_RATES)
