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


def make_package(basket_dict: dict):
    return {"weight": {"value": get_weight(basket_dict), "unit": "ounce"}}


def make_SE_shipment(basket_dict, address_dict):
    shipment_dict = init_SE_shipment_dict()
    shipment_dict["shipment"]["ship_to"] = address_dict
    shipment_dict["shipment"]["packages"].append(make_package(basket_dict))

    return shipment_dict


def get_rates(engine, shipment):
    response = engine.get_rates_from_shipment(shipment)
    logger.warning(f"SE returned:\n{response}")
    if response.get("rate_response").get("rates"):
        return response.get("rate_response").get("rates")
    else:
        return response.get("rate_response").get("invalid_rates")


def shipping_choices_SS(basket: Basket, address_dict: dict):
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
            "toState": address_dict["state_province"],
            "toCity": address_dict["city_locality"],
            "toPostalCode": address_dict["postal_code"],
            "toCountry": address_dict["country_code"],
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
    shipment = make_SE_shipment(basket, address_d)

    try:
        get_rates_response = get_rates(shipengine, shipment)
        logger.warning("FULL SE RESPONSE:\n{get_rates_response}")
        return list(map(lambda r: rate_to_choice(r), get_rates_response))
    except ShipEngineError as err:
        logger.error("==== ERROR calling ShipEngine")
        logger.error(err.to_json())


# these are just to quiet the code
# true = True
# false = False
# null = None

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

# SE response with invalid rates
{
    "rate_response": {
        "rates": [],
        "invalid_rates": [
            {
                "rate_id": "se-5981118302",
                "rate_type": "shipment",
                "carrier_id": "se-660216",
                "shipping_amount": {"currency": "usd", "amount": 116.56},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 25.35},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "Shipping",
                        "carrier_billing_code": "BaseServiceCharge",
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 116.56},
                        "billing_source": "Carrier",
                    },
                    {
                        "rate_detail_type": "fuel_charge",
                        "carrier_description": "Fuel Surcharge",
                        "carrier_billing_code": "375",
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 25.35},
                        "billing_source": "Carrier",
                    },
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 1,
                "guaranteed_service": True,
                "estimated_delivery_date": "2024-10-01T13:30:00Z",
                "carrier_delivery_days": "Tuesday 10/1 by 01:30 PM",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "UPS Worldwide Express®",
                "service_code": "ups_worldwide_express",
                "trackable": True,
                "carrier_code": "ups",
                "carrier_nickname": "ShipEngine Test Account - UPS",
                "carrier_friendly_name": "UPS",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118303",
                "rate_type": "shipment",
                "carrier_id": "se-660216",
                "shipping_amount": {"currency": "usd", "amount": 104.93},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 22.82},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "Shipping",
                        "carrier_billing_code": "BaseServiceCharge",
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 104.93},
                        "billing_source": "Carrier",
                    },
                    {
                        "rate_detail_type": "fuel_charge",
                        "carrier_description": "Fuel Surcharge",
                        "carrier_billing_code": "375",
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 22.82},
                        "billing_source": "Carrier",
                    },
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 2,
                "guaranteed_service": True,
                "estimated_delivery_date": "2024-10-02T23:30:00Z",
                "carrier_delivery_days": "Wednesday 10/2 by 11:30 PM",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "UPS Worldwide Expedited®",
                "service_code": "ups_worldwide_expedited",
                "trackable": True,
                "carrier_code": "ups",
                "carrier_nickname": "ShipEngine Test Account - UPS",
                "carrier_friendly_name": "UPS",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118304",
                "rate_type": "shipment",
                "carrier_id": "se-660216",
                "shipping_amount": {"currency": "usd", "amount": 25.41},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 4.95},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "Shipping",
                        "carrier_billing_code": "BaseServiceCharge",
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 25.41},
                        "billing_source": "Carrier",
                    },
                    {
                        "rate_detail_type": "fuel_charge",
                        "carrier_description": "Fuel Surcharge",
                        "carrier_billing_code": "375",
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 4.95},
                        "billing_source": "Carrier",
                    },
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 3,
                "guaranteed_service": True,
                "estimated_delivery_date": "2024-10-03T23:30:00Z",
                "carrier_delivery_days": "Thursday 10/3 by 11:30 PM",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "UPS Standard®",
                "service_code": "ups_standard_international",
                "trackable": True,
                "carrier_code": "ups",
                "carrier_nickname": "ShipEngine Test Account - UPS",
                "carrier_friendly_name": "UPS",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118305",
                "rate_type": "shipment",
                "carrier_id": "se-660216",
                "shipping_amount": {"currency": "usd", "amount": 116.56},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 25.35},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "Shipping",
                        "carrier_billing_code": "BaseServiceCharge",
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 116.56},
                        "billing_source": "Carrier",
                    },
                    {
                        "rate_detail_type": "fuel_charge",
                        "carrier_description": "Fuel Surcharge",
                        "carrier_billing_code": "375",
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 25.35},
                        "billing_source": "Carrier",
                    },
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 1,
                "guaranteed_service": True,
                "estimated_delivery_date": "2024-10-01T10:30:00Z",
                "carrier_delivery_days": "Tuesday 10/1 by 10:30 AM",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "UPS Worldwide Express Plus®",
                "service_code": "ups_worldwide_express_plus",
                "trackable": True,
                "carrier_code": "ups",
                "carrier_nickname": "ShipEngine Test Account - UPS",
                "carrier_friendly_name": "UPS",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118306",
                "rate_type": "shipment",
                "carrier_id": "se-660216",
                "shipping_amount": {"currency": "usd", "amount": 112.07},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 24.38},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "Shipping",
                        "carrier_billing_code": "BaseServiceCharge",
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 112.07},
                        "billing_source": "Carrier",
                    },
                    {
                        "rate_detail_type": "fuel_charge",
                        "carrier_description": "Fuel Surcharge",
                        "carrier_billing_code": "375",
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 24.38},
                        "billing_source": "Carrier",
                    },
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 1,
                "guaranteed_service": True,
                "estimated_delivery_date": "2024-10-01T23:30:00Z",
                "carrier_delivery_days": "Tuesday 10/1 by 11:30 PM",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "UPS Worldwide Saver®",
                "service_code": "ups_worldwide_saver",
                "trackable": True,
                "carrier_code": "ups",
                "carrier_nickname": "ShipEngine Test Account - UPS",
                "carrier_friendly_name": "UPS",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118307",
                "rate_type": "shipment",
                "carrier_id": "se-660217",
                "shipping_amount": {"currency": "usd", "amount": 118.26},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 6.96},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "uncategorized",
                        "carrier_description": "Demand Surcharge",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 1.0},
                        "billing_source": "Carrier",
                    },
                    {
                        "rate_detail_type": "fuel_charge",
                        "carrier_description": "Fuel",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 5.96},
                        "billing_source": "Carrier",
                    },
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "Total Net Freight",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 118.26},
                        "billing_source": "Carrier",
                    },
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 1,
                "guaranteed_service": False,
                "estimated_delivery_date": "2024-10-01T12:00:00Z",
                "carrier_delivery_days": "Tuesday 10/1 by 12:00 PM",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "FedEx International Priority Express®",
                "service_code": "fedex_international_priority_express",
                "trackable": True,
                "carrier_code": "fedex",
                "carrier_nickname": "ShipEngine Test Account - FedEx",
                "carrier_friendly_name": "FedEx",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118308",
                "rate_type": "shipment",
                "carrier_id": "se-660217",
                "shipping_amount": {"currency": "usd", "amount": 112.95},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 10.9},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "uncategorized",
                        "carrier_description": "Demand Surcharge",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 5.0},
                        "billing_source": "Carrier",
                    },
                    {
                        "rate_detail_type": "fuel_charge",
                        "carrier_description": "Fuel",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 5.9},
                        "billing_source": "Carrier",
                    },
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "Total Net Freight",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 112.95},
                        "billing_source": "Carrier",
                    },
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 1,
                "guaranteed_service": False,
                "estimated_delivery_date": "2024-10-01T17:00:00Z",
                "carrier_delivery_days": "Tuesday 10/1 by 05:00 PM",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "FedEx International Priority®",
                "service_code": "fedex_international_priority",
                "trackable": False,
                "carrier_code": "fedex",
                "carrier_nickname": "ShipEngine Test Account - FedEx",
                "carrier_friendly_name": "FedEx",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118309",
                "rate_type": "shipment",
                "carrier_id": "se-660217",
                "shipping_amount": {"currency": "usd", "amount": 106.69},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 6.38},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "uncategorized",
                        "carrier_description": "Demand Surcharge",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 1.0},
                        "billing_source": "Carrier",
                    },
                    {
                        "rate_detail_type": "fuel_charge",
                        "carrier_description": "Fuel",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 5.38},
                        "billing_source": "Carrier",
                    },
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "Total Net Freight",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 106.69},
                        "billing_source": "Carrier",
                    },
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 2,
                "guaranteed_service": False,
                "estimated_delivery_date": "2024-10-02T17:00:00Z",
                "carrier_delivery_days": "Wednesday 10/2 by 05:00 PM",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "FedEx International Economy®",
                "service_code": "fedex_international_economy",
                "trackable": True,
                "carrier_code": "fedex",
                "carrier_nickname": "ShipEngine Test Account - FedEx",
                "carrier_friendly_name": "FedEx",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118310",
                "rate_type": "shipment",
                "carrier_id": "se-660217",
                "shipping_amount": {"currency": "usd", "amount": 98.69},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 4.93},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "fuel_charge",
                        "carrier_description": "Fuel",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 4.93},
                        "billing_source": "Carrier",
                    },
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "Total Net Freight",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 98.69},
                        "billing_source": "Carrier",
                    },
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 3,
                "guaranteed_service": False,
                "estimated_delivery_date": "2024-10-03T22:00:00Z",
                "carrier_delivery_days": "Thursday 10/3 by 10:00 PM",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "FedEx International Connect Plus®",
                "service_code": "fedex_international_connect_plus",
                "trackable": False,
                "carrier_code": "fedex",
                "carrier_nickname": "ShipEngine Test Account - FedEx",
                "carrier_friendly_name": "FedEx",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118311",
                "rate_type": "shipment",
                "carrier_id": "se-660217",
                "shipping_amount": {"currency": "usd", "amount": 25.45},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 1.65},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "fuel_charge",
                        "carrier_description": "FedEx Ground Fuel",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 1.65},
                        "billing_source": "Carrier",
                    },
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "Total Net Freight",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 25.45},
                        "billing_source": "Carrier",
                    },
                ],
                "zone": 51,
                "package_type": "package",
                "delivery_days": 3,
                "guaranteed_service": False,
                "estimated_delivery_date": "2024-10-03T23:59:00Z",
                "carrier_delivery_days": "3",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "FedEx International Ground®",
                "service_code": "fedex_ground_international",
                "trackable": True,
                "carrier_code": "fedex",
                "carrier_nickname": "ShipEngine Test Account - FedEx",
                "carrier_friendly_name": "FedEx",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118312",
                "rate_type": "shipment",
                "carrier_id": "se-660215",
                "shipping_amount": {"currency": "usd", "amount": 16.46},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 0.0},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "shipping",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 16.46},
                        "billing_source": "Carrier",
                    }
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": None,
                "guaranteed_service": False,
                "estimated_delivery_date": None,
                "carrier_delivery_days": None,
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "USPS First Class Mail Intl",
                "service_code": "usps_first_class_mail_international",
                "trackable": False,
                "carrier_code": "stamps_com",
                "carrier_nickname": "ShipEngine Test Account - Stamps.com",
                "carrier_friendly_name": "Stamps.com",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118313",
                "rate_type": "shipment",
                "carrier_id": "se-660215",
                "shipping_amount": {"currency": "usd", "amount": 40.91},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 0.0},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "shipping",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 40.91},
                        "billing_source": "Carrier",
                    }
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 10,
                "guaranteed_service": False,
                "estimated_delivery_date": "2024-10-10T00:00:00Z",
                "carrier_delivery_days": "6 - 10",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "USPS Priority Mail Intl",
                "service_code": "usps_priority_mail_international",
                "trackable": False,
                "carrier_code": "stamps_com",
                "carrier_nickname": "ShipEngine Test Account - Stamps.com",
                "carrier_friendly_name": "Stamps.com",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118314",
                "rate_type": "shipment",
                "carrier_id": "se-660215",
                "shipping_amount": {"currency": "usd", "amount": 57.32},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 0.0},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "shipping",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 57.32},
                        "billing_source": "Carrier",
                    }
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 5,
                "guaranteed_service": False,
                "estimated_delivery_date": "2024-10-05T00:00:00Z",
                "carrier_delivery_days": "3 - 5",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "USPS Priority Mail Express Intl",
                "service_code": "usps_priority_mail_express_international",
                "trackable": False,
                "carrier_code": "stamps_com",
                "carrier_nickname": "ShipEngine Test Account - Stamps.com",
                "carrier_friendly_name": "Stamps.com",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118315",
                "rate_type": "shipment",
                "carrier_id": "se-660215",
                "shipping_amount": {"currency": "usd", "amount": 13.04},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 0.0},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "shipping",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 13.04},
                        "billing_source": "Carrier",
                    }
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 14,
                "guaranteed_service": False,
                "estimated_delivery_date": "2024-10-14T00:00:00Z",
                "carrier_delivery_days": "7-14",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "GlobalPost Economy Intl",
                "service_code": "globalpost_economy",
                "trackable": False,
                "carrier_code": "stamps_com",
                "carrier_nickname": "ShipEngine Test Account - Stamps.com",
                "carrier_friendly_name": "Stamps.com",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118316",
                "rate_type": "shipment",
                "carrier_id": "se-660215",
                "shipping_amount": {"currency": "usd", "amount": 12.69},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 0.0},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "shipping",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 12.69},
                        "billing_source": "Carrier",
                    }
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 10,
                "guaranteed_service": False,
                "estimated_delivery_date": "2024-10-10T00:00:00Z",
                "carrier_delivery_days": "6-10",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "GlobalPost Standard Intl",
                "service_code": "globalpost_priority",
                "trackable": False,
                "carrier_code": "stamps_com",
                "carrier_nickname": "ShipEngine Test Account - Stamps.com",
                "carrier_friendly_name": "Stamps.com",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
            {
                "rate_id": "se-5981118317",
                "rate_type": "shipment",
                "carrier_id": "se-660215",
                "shipping_amount": {"currency": "usd", "amount": 11.5},
                "insurance_amount": {"currency": "usd", "amount": 0.0},
                "confirmation_amount": {"currency": "usd", "amount": 0.0},
                "other_amount": {"currency": "usd", "amount": 0.0},
                "requested_comparison_amount": {
                    "currency": "usd",
                    "amount": 0.0,
                },
                "rate_details": [
                    {
                        "rate_detail_type": "shipping",
                        "carrier_description": "shipping",
                        "carrier_billing_code": None,
                        "carrier_memo": None,
                        "amount": {"currency": "usd", "amount": 11.5},
                        "billing_source": "Carrier",
                    }
                ],
                "zone": None,
                "package_type": "package",
                "delivery_days": 5,
                "guaranteed_service": False,
                "estimated_delivery_date": "2024-10-05T00:00:00Z",
                "carrier_delivery_days": "3-5",
                "ship_date": "2024-09-30T00:00:00Z",
                "negotiated_rate": False,
                "service_type": "GlobalPost Plus",
                "service_code": "gp_plus",
                "trackable": False,
                "carrier_code": "stamps_com",
                "carrier_nickname": "ShipEngine Test Account - Stamps.com",
                "carrier_friendly_name": "Stamps.com",
                "validation_status": "invalid",
                "warning_messages": [],
                "error_messages": [
                    "No customs items have been created for international order."
                ],
            },
        ],
        "rate_request_id": "se-851476958",
        "shipment_id": "se-1504763950",
        "created_at": "2024-09-30T05:09:40.6337917Z",
        "status": "completed",
        "errors": [],
    },
    "shipment_id": "se-1504763950",
    "carrier_id": None,
    "service_code": None,
    "external_shipment_id": None,
    "shipment_number": None,
    "ship_date": "2024-09-30T00:00:00Z",
    "created_at": "2024-09-30T05:09:36.293Z",
    "modified_at": "2024-09-30T05:09:36.28Z",
    "shipment_status": "pending",
    "ship_to": {
        "geolocation": None,
        "instructions": "",
        "name": "",
        "phone": "6478936710",
        "email": None,
        "company_name": None,
        "address_line1": "250 Cassandra Blvd",
        "address_line2": "apt 232",
        "address_line3": None,
        "city_locality": "Toronto",
        "state_province": "ON",
        "postal_code": "M3A1T8",
        "country_code": "CA",
        "address_residential_indicator": "unknown",
    },
    "ship_from": {
        "instructions": None,
        "name": "Shipping department",
        "phone": "617-734-0608",
        "email": None,
        "company_name": "Holy Transfiguration Monastery",
        "address_line1": "278 Warren St",
        "address_line2": None,
        "address_line3": None,
        "city_locality": "Brookline",
        "state_province": "MA",
        "postal_code": "02445",
        "country_code": "US",
        "address_residential_indicator": "no",
    },
    "warehouse_id": None,
    "return_to": {
        "instructions": None,
        "name": "Shipping department",
        "phone": "617-734-0608",
        "email": None,
        "company_name": "Holy Transfiguration Monastery",
        "address_line1": "278 Warren St",
        "address_line2": None,
        "address_line3": None,
        "city_locality": "Brookline",
        "state_province": "MA",
        "postal_code": "02445",
        "country_code": "US",
        "address_residential_indicator": "no",
    },
    "is_return": False,
    "confirmation": "none",
    "customs": {
        "contents": "merchandise",
        "contents_explanation": None,
        "customs_items": [],
        "non_delivery": "return_to_sender",
        "buyer_shipping_amount_paid": None,
        "duties_paid": None,
        "terms_of_trade_code": None,
        "declaration": None,
        "invoice_additional_details": {
            "freight_charge": None,
            "insurance_charge": None,
            "other_charge": None,
            "other_charge_description": None,
            "discount": None,
        },
        "importer_of_record": None,
        "export_declaration_number": None,
    },
    "external_order_id": None,
    "order_source_code": None,
    "advanced_options": {
        "bill_to_account": None,
        "bill_to_country_code": None,
        "bill_to_party": None,
        "bill_to_postal_code": None,
        "contains_alcohol": False,
        "delivered_duty_paid": False,
        "non_machinable": False,
        "saturday_delivery": False,
        "dry_ice": False,
        "dry_ice_weight": None,
        "fedex_freight": None,
        "third_party_consignee": False,
        "ancillary_endorsements_option": None,
        "freight_class": None,
        "custom_field1": None,
        "custom_field2": None,
        "custom_field3": None,
        "collect_on_delivery": None,
        "return_pickup_attempts": None,
        "additional_handling": False,
        "own_document_upload": False,
        "limited_quantity": False,
        "event_notification": False,
    },
    "comparison_rate_type": None,
    "retail_rate": None,
    "shipping_rule_id": None,
    "insurance_provider": "none",
    "tags": [],
    "packages": [
        {
            "shipment_package_id": "se-1767201776",
            "package_id": "se-3",
            "package_code": "package",
            "package_name": "Package",
            "weight": {"value": 1.22, "unit": "ounce"},
            "dimensions": {
                "unit": "inch",
                "length": 0.0,
                "width": 0.0,
                "height": 0.0,
            },
            "insured_value": {"currency": "usd", "amount": 0.0},
            "label_messages": {
                "reference1": None,
                "reference2": None,
                "reference3": None,
            },
            "external_package_id": None,
            "content_description": None,
            "products": [],
        }
    ],
    "total_weight": {"value": 1.22, "unit": "ounce"},
    "items": [],
}
