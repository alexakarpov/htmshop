import json
import logging
import requests

from dotenv import dotenv_values

from django.conf import settings
from shipengine import ShipEngine
from shipengine.errors import ShipEngineError

from ecommerce.apps.basket.basket import Basket, get_weight

from .choice import rate_to_choice, ShippingChoiceSS

logger = logging.getLogger(__name__)

shipengine = ShipEngine(
    {
        "api_key": settings.SE_API_KEY,
        "page_size": 75,
        "retries": 3,
        "timeout": 10,
    }
)

init_SS_dict = {
    "fromPostalCode": "02445",
    "fromCity": "Brookline",
    "fromState": "MA",
}


def init_SE_shipment_dict():
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
                # TODO: # "usps_media_mail", # add for books-only basket
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


def make_SE_shipment(basketd, address_d):
    sd = init_SE_shipment_dict()
    sd["shipment"]["ship_to"] = address_d
    sd["shipment"]["packages"].append(make_package(basketd))
    return sd


def get_rates(engine, shipment):
    response = engine.get_rates_from_shipment(shipment)
    logger.warning(f"SE returned:\n{response}")
    if response.get("rate_response").get("rates"):
        return response


def shipping_choices_SS(basket: Basket, address_d: dict):
    ss_dict = init_SS_dict
    config = dotenv_values()
    auth = (config["SS_API_KEY"], config["SS_API_SECRET"])
    weight = get_weight(basket)
    logger.warning(f"weight calculated as {weight}")
    ss_dict.update(
        {
            "weight": {"value": weight, "unit": "ounces"},
            "packageCode": "package",
            "carrierCode": "stamps_com",
            "toState": address_d["state_province"],
            "toCity": address_d["city_locality"],
            "toPostalCode": address_d["postal_code"],
            "toCountry": address_d["country_code"],
        }
    )

    # USPS
    usps_response = requests.post(
        settings.SS_GET_RATES_URL, json=ss_dict, auth=auth
    )

    json_usps = json.loads(usps_response.text)
    choices = []
    for it in json_usps:
        print(it)
        serviceCode = it["serviceCode"]
        cost = it["shipmentCost"]
        choices.append(ShippingChoiceSS(serviceCode, cost))

    # UPS
    ss_dict.update({"carrierCode": "ups"})
    ups_response = requests.post(
        settings.SS_GET_RATES_URL, json=ss_dict, auth=auth
    )

    json_ups = json.loads(ups_response.text)

    for it in json_ups:
        print(it)
        serviceCode = it["serviceCode"]
        cost = it["shipmentCost"]
        choices.append(ShippingChoiceSS(serviceCode, cost))

    return choices


def shipping_choices_SE(basket: Basket, address_d: dict):
    # @TODO: if address is international, need customs data

    shipment = make_SE_shipment(basket, address_d)
    logger.warning(f"built shipment:\n{shipment}")
    rates = []

    try:
        if se_response := get_rates(shipengine, shipment):
            rates = se_response.get("rate_response").get("rates")
            return list(map(lambda r: rate_to_choice(r), rates))
        else:
            print("OOPS")
            return []
    except ShipEngineError as err:
        logger.error("==== ERROR calling ShipEngine")
        logger.error(err.to_json())


# these are just to quiet the code
true = True
false = False
null = None

SS_GET_CARRIERS_RESPONSE = [
    {
        "name": "Stamps.com",
        "code": "stamps_com",
        "accountNumber": "frmichael",
        "requiresFundedAccount": true,
        "balance": 315.1316,
        "nickname": "Stamps-FM",
        "shippingProviderId": 127005,
        "primary": true,
    },
    {
        "name": "UPS",
        "code": "ups",
        "accountNumber": "039128",
        "requiresFundedAccount": false,
        "balance": 0.0,
        "nickname": null,
        "shippingProviderId": 265492,
        "primary": true,
    },
    {
        "name": "FedEx",
        "code": "fedex",
        "accountNumber": "200784219",
        "requiresFundedAccount": false,
        "balance": 0.0,
        "nickname": "FEDEX",
        "shippingProviderId": 142514,
        "primary": true,
    },
    {
        "name": "DHL Express from ShipStation",
        "code": "dhl_express_worldwide",
        "accountNumber": null,
        "requiresFundedAccount": true,
        "balance": 315.1316,
        "nickname": "Stamps-FM",
        "shippingProviderId": 162523,
        "primary": true,
    },
    {
        "name": "UPS by ShipStation",
        "code": "ups_walleted",
        "accountNumber": "F87387",
        "requiresFundedAccount": true,
        "balance": 315.1316,
        "nickname": "Stamps-FM",
        "shippingProviderId": 127012,
        "primary": true,
    },
    {
        "name": "SEKO LTL by ShipStation",
        "code": "seko_ltl_walleted",
        "accountNumber": null,
        "requiresFundedAccount": true,
        "balance": 315.1316,
        "nickname": "Stamps-FM",
        "shippingProviderId": 264642,
        "primary": true,
    },
    {
        "name": "DHL eCommerce by ShipStation",
        "code": "dhl_ecommerce_wallet",
        "accountNumber": "8781258a-e9f1-404c-81f9-cf1ae13472d1",
        "requiresFundedAccount": true,
        "balance": 315.1316,
        "nickname": "Stamps-FM",
        "shippingProviderId": 662913,
        "primary": true,
    },
    {
        "name": "GlobalPost",
        "code": "globalpost",
        "accountNumber": "72732fc7-76d9-4aea-a56c-b84dfd9b5114",
        "requiresFundedAccount": true,
        "balance": 315.1316,
        "nickname": "Stamps-FM",
        "shippingProviderId": 405013,
        "primary": true,
    },
]

SS_GET_RATES_RESPONSE = [
    {
        "serviceName": "USPS First Class Mail - Large Envelope or Flat",
        "serviceCode": "usps_first_class_mail",
        "shipmentCost": 4.0100,
        "otherCost": 0.0,
    },
    {
        "serviceName": "USPS First Class Mail - Package",
        "serviceCode": "usps_first_class_mail",
        "shipmentCost": 5.6200,
        "otherCost": 0.0,
    },
    {
        "serviceName": "USPS Priority Mail - Package",
        "serviceCode": "usps_priority_mail",
        "shipmentCost": 10.0700,
        "otherCost": 0.0,
    },
    {
        "serviceName": "USPS Priority Mail - Medium Flat Rate Box",
        "serviceCode": "usps_priority_mail",
        "shipmentCost": 15.1900,
        "otherCost": 0.0,
    },
    {
        "serviceName": "USPS Priority Mail - Small Flat Rate Box",
        "serviceCode": "usps_priority_mail",
        "shipmentCost": 8.7100,
        "otherCost": 0.0,
    },
    {
        "serviceName": "USPS Priority Mail - Large Flat Rate Box",
        "serviceCode": "usps_priority_mail",
        "shipmentCost": 20.6900,
        "otherCost": 0.0,
    },
    {
        "serviceName": "USPS Priority Mail - Flat Rate Envelope",
        "serviceCode": "usps_priority_mail",
        "shipmentCost": 8.1800,
        "otherCost": 0.0,
    },
    {
        "serviceName": "USPS Priority Mail - Flat Rate Padded Envelope",
        "serviceCode": "usps_priority_mail",
        "shipmentCost": 8.9500,
        "otherCost": 0.0,
    },
    {
        "serviceName": "USPS Priority Mail Express - Package",
        "serviceCode": "usps_priority_mail_express",
        "shipmentCost": 47.2500,
        "otherCost": 0.0,
    },
    {
        "serviceName": "USPS Priority Mail Express - Flat Rate Envelope",
        "serviceCode": "usps_priority_mail_express",
        "shipmentCost": 26.3500,
        "otherCost": 0.0,
    },
    {
        "serviceName": "USPS Priority Mail Express - Flat Rate Padded Envelope",
        "serviceCode": "usps_priority_mail_express",
        "shipmentCost": 26.8500,
        "otherCost": 0.0,
    },
    {
        "serviceName": "USPS Media Mail - Package",
        "serviceCode": "usps_media_mail",
        "shipmentCost": 4.6300,
        "otherCost": 0.0,
    },
    {
        "serviceName": "USPS Ground Advantage - Package",
        "serviceCode": "usps_ground_advantage",
        "shipmentCost": 5.6200,
        "otherCost": 0.0,
    },
]

# invalid rates response

# request with customs info
