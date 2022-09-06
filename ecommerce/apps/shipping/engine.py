from .choice import ShippingChoice, rate_to_choice
from shipengine.errors import ShipEngineError
from ecommerce.utils import debug_print

import json
import time
import logging

from django.conf import settings
from ecommerce.apps.basket.basket import get_weight
from shipengine import ShipEngine

logger = logging.getLogger("django")

shipengine = ShipEngine(
    {
        "api_key": settings.SE_API_KEY,
        "page_size": 75,
        "retries": 3,
        "timeout": 10,
    }
)


def init_shipment_dict():
    return {
        "rate_options": {
            "carrier_ids": [
                settings.USPS_ID,
                settings.FEDEX_ID,
                settings.UPS_ID,
            ],
            "service_codes": [
                # USPS
                # "usps_priority_mail_express",
                # "usps_parcel_select",
                # "usps_first_class_mail",
                # "usps_media_mail", # add for books-only basket
            ],
            "package_types": ["package"],
        },
        "shipment": {
            "ship_from": {
                "name": "Shipping department",
                "company_name": "Holy Transfiguration Monastery",
                "phone": "617-734-0608",
                "address_line1": "278 Warren St",
                "city_locality": "Brookline",
                "state_province": "MA",
                "postal_code": "02445",
                "country_code": "US",
                "address_residential_indicator": "yes",
            },
            "ship_to": {},
            "packages": [],
        },
    }


def make_package(basketd):
    return {"weight": {"value": get_weight(basketd), "unit": "ounce"}}


def make_shipment(basketd, address):
    sd = init_shipment_dict()
    sd["shipment"]["ship_to"]["name"] = address.full_name
    sd["shipment"]["ship_to"]["phone"] = address.phone
    sd["shipment"]["ship_to"]["address_line1"] = address.address_line
    sd["shipment"]["ship_to"]["address_line2"] = address.address_line2
    sd["shipment"]["ship_to"]["city_locality"] = address.town_city
    sd["shipment"]["ship_to"]["state_province"] = address.state_province
    sd["shipment"]["ship_to"]["postal_code"] = address.postcode
    sd["shipment"]["ship_to"]["country_code"] = address.country
    sd["shipment"]["packages"].append(make_package(basketd))
    return sd


def get_rates(engine, shipment):
    return engine.get_rates_from_shipment(shipment)


def shipping_choices(basket, address):
    logger.debug(basket)
    logger.debug(address.toJSON())
    shipment = make_shipment(basket, address)
    logger.debug(shipment)
    se_response = get_rates(shipengine, shipment)
    rates = se_response.get("rate_response").get("rates")
    # rates = None
    # with open("shipping_jsons/get_rates_response.json", "r") as f:
    #     rates = json.load(f).get("rate_response").get("rates")
    # time.sleep(1)
    choices = list(map(lambda r: rate_to_choice(r), rates))

    return choices
