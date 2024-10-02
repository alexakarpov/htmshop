import json
from unittest.mock import patch

# Third-party imports...
from rest_framework.test import APIRequestFactory, APITestCase

from ecommerce.apps.accounts.models import Address
from ecommerce.apps.shipping.views import get_rates

from .choice import ShippingChoiceSE, rate_to_choice, split_tiers_SE
from .engine import make_SE_shipment
from .serializers import ShippingChoiceSESerializer
from ecommerce.apps.shipping.engine import shipping_choices_SE

# import unittest

test_cart = [
    {
        "price": "30.00",
        "qty": 1,
        "variant": "8x10",
        "title": "Holy Napkin",
        "weight": 16,
    },
    {
        "price": "20.00",
        "qty": 1,
        "variant": "",
        "title": "Prayer Book",
        "weight": 8,
    },
]

test_address = Address()
test_address.full_name = "John Doe"
test_address.address_line1 = "1 Main St"
test_address.postcode = "98765"
test_address.town_city = "Boston"


class SimpleTest(APITestCase):
    fixtures = ["accounts.json"]

    def test_api(self):
        factory = APIRequestFactory()
        request = factory.get("/shipping/get-rates/")
        request.session = {}

        address = Address.objects.first()
        aj = address.toJSON()

        request.session["address"] = aj
        view = get_rates
        assert Address.objects.count() == 1
        response = view(request)
        print(f"RESPONSE CAME:\n{response.content}\n=======")
        choices_j = json.loads(response.content).get("choices")
        self.assertEqual(len(choices_j), 3)
        self.assertEqual(choices_j[0].get("name"), "Regular")
        self.assertEqual(choices_j[0].get("id"), "se-1573559620")

    def test_make_shipment(self):
        s = make_SE_shipment(test_cart, test_address.to_dict())
        sd = s["shipment"]
        assert (
            sd["ship_from"]["company_name"] == "Holy Transfiguration Monastery"
        )
        assert sd["ship_to"]["postal_code"] == test_address.postcode
        assert sd["ship_to"]["full_name"] == test_address.full_name
        assert sd["ship_to"]["country_code"] == test_address.country == "US"
        assert sd["ship_to"]["city_locality"] == test_address.town_city
        assert sd.get("packages") == [
            {"weight": {"value": 24, "unit": "ounce"}}
        ]

    def test_rate_to_choice(self):
        with open("shipping_jsons/rate.json", "r") as f:
            rate = json.load(f)
            choice = rate_to_choice(rate)
            assert choice.price == 17.74
            assert choice.name == "usps_priority_mail"

    def test_tiers(self):
        r1 = {
            "rate_id": "se-123",
            "shipping_amount": {"amount": 17.74},
            "delivery_days": 5,
            "service_code": "fedex_standard_overnight",  # expedite
        }
        r2 = {
            "rate_id": "se-231",
            "shipping_amount": {"amount": 27.29},
            "delivery_days": 3,
            "service_code": "usps_priority_mail",  # regular
        }
        r3 = {
            "rate_id": "se-145",
            "shipping_amount": {"amount": 37.29},
            "delivery_days": 1,
            "service_code": "fedex_2day",  # fast
        }

        choices = list(map(lambda r: rate_to_choice(r), [r1, r2, r3]))
        tiers = split_tiers_SE(choices)
        self.assertEqual(choices[0].price, 17.74)
        assert choices[0].name == "fedex_standard_overnight"
        assert tiers["regular"][0].name == "usps_priority_mail"
        assert tiers["fast"][0].name == "fedex_2day"
        assert tiers["express"][0].name == "fedex_standard_overnight"

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
        tiers = split_tiers_SE(choices, international=True)
        self.assertEqual(3, len(tiers.values()))

        print(tiers)

    def test_shipping_choice_seriaizer(self):
        c = ShippingChoiceSE("nameo", 21.99, "qwe123", 9)
        ser = ShippingChoiceSESerializer(c)
        assert ser.data.get("name") == "nameo"
        assert ser.data.get("price") == 21.99
        assert ser.data.get("id") == "qwe123"
        assert ser.data.get("days") == 9

    @patch("ecommerce.apps.shipping.engine.shipengine.get_rates_from_shipment")
    def test_shipping_choices(self, mock_get_rates_from_shipment):
        with open("shipping_jsons/get_rates_response.json", "r") as f:
            rresponse = json.load(f)

        mock_get_rates_from_shipment.return_value = rresponse
        choices = shipping_choices_SE(test_cart, test_address)

        # TODO: work out a proper assertion
        c1 = ShippingChoiceSE.from_repr(
            "usps_priority_mail/20.77/se-1573559617/2"
        )
        self.assertEqual(len(choices), 18)
        self.assertIn(c1, choices)
