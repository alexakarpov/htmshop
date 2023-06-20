import json
import logging

from django.conf import settings
from shipengine import ShipEngine
from shipengine.errors import ShipEngineError

from ecommerce.apps.accounts.models import Address
from ecommerce.apps.basket.basket import Basket, get_weight

from .choice import rate_to_choice

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


def make_package(basketd: dict):
    return {"weight": {"value": get_weight(basketd), "unit": "ounce"}}


def make_shipment(basketd, address_d):
    sd = init_shipment_dict()
    # sd["shipment"]["ship_to"]["country_code"] = address.country
    sd["shipment"]["ship_to"] = address_d
    sd["shipment"]["packages"].append(make_package(basketd))
    return sd


def get_rates(engine, shipment):
    return engine.get_rates_from_shipment(shipment)


def shipping_choices(basket: Basket, address_d: dict):
    shipment = make_shipment(basket, address_d)
    logger.debug(f"built shipment:\n{shipment}")
    rates = []
    # TODO: go back to calling SE
    # try:
    #     se_response = get_rates(shipengine, shipment)
    #     rates = se_response.get("rate_response").get("rates")
    # except ShipEngineError as err:
    #     logger.error(err.to_json())

    rates = None
    with open("shipping_jsons/get_rates_response.json", "r") as f:
        rates = json.load(f).get("rate_response").get("rates")

    choices = list(map(lambda r: rate_to_choice(r), rates))
    return choices
