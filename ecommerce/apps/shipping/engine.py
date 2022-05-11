import json

from django.conf import settings
from shipengine import ShipEngine

shipengine = ShipEngine({"api_key": settings.SE_API_KEY, "page_size": 75, "retries": 3, "timeout": 10})

from shipengine.errors import ShipEngineError


def init_shipment_dict():
    return {
        "rate_options": {
            "carrier_ids": [
                settings.USPS_ID,
            ],
            "service_codes": [
                "usps_priority_mail_express",
                "usps_parcel_select",
                "usps_first_class_mail",
                "usps_media_mail",
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


def make_shipment(basket, address):
    sd = init_shipment_dict()
    sd["shipment"]["ship_to"]["name"] = address.full_name
    sd["shipment"]["ship_to"]["phone"] = address.phone
    sd["shipment"]["ship_to"]["address_line1"] = address.address_line
    sd["shipment"]["ship_to"]["address_line2"] = address.address_line2
    sd["shipment"]["ship_to"]["city_locality"] = address.town_city
    sd["shipment"]["ship_to"]["state_province"] = address.state_province
    sd["shipment"]["ship_to"]["postal_code"] = address.postcode
    sd["shipment"]["ship_to"]["country_code"] = address.country

    return sd
