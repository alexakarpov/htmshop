import json
import logging
import requests

from dotenv import dotenv_values

from django.conf import settings
from shipengine import ShipEngine
from shipengine.errors import ShipEngineError

from ecommerce.apps.basket.basket import Basket, get_weight
from ecommerce.apps.orders.models import Order
from ecommerce.constants import PACKING_WEIGHT_MULTIPLIER

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
                # "usps_priority_mail_express",
                # "usps_parcel_select",
                # "usps_first_class_mail",
                # TODO: # "usps_media_mail", # add for books-only basket
            ],
            "package_code": "package",
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
            "packages": [],  # required to append to!
        },
    }


def get_order_weight(order):
    total = sum(
        item.stock.weight * item.quantity for item in order.items.all()
    )
    return float(total) * float(PACKING_WEIGHT_MULTIPLIER)


def order_to_package(order: Order):
    return {
        "weight": {
            "value": get_order_weight(order),
            "unit": "ounce",
        }
    }


def make_package(basket_dict: dict):
    return {
        "weight": {
            "value": get_weight(basket_dict),
            "unit": "ounce",
        }
    }


def make_shipment_for_order(order: Order):
    international = order.country_code != "US"
    shipment_dict = init_SE_shipment_dict()
    shipment_dict["shipment"]["packages"] = [order_to_package(order)]
    shipment_dict["shipment"]["ship_to"] = order.extract_ship_to()
    shipment_dict["rate_options"] = {
        "carrier_ids": [settings.USPS_ID, settings.UPS_ID, settings.FEDEX_ID],
        "package_types": ["package"],
    }

    codes = (
        settings.INTL_REGULAR + settings.INTL_FAST + settings.INTL_EXPRESS
        if international
        else settings.REGULAR + settings.FAST + settings.EXPRESS
    )
    if order.is_media() and not international:
            codes.append(settings.USPS_MEDIA_MAIL)
    shipment_dict["rate_options"].update({"service_codes": codes})
    return shipment_dict


def make_SE_shipment(basket, address_dict):
    international = address_dict.get("country_code") != "US"
    shipment_dict = init_SE_shipment_dict()
    shipment_dict["shipment"]["ship_to"] = address_dict
    shipment_dict["shipment"]["packages"] = [make_package(basket)]

    shipment_dict["rate_options"] = {
        "carrier_ids": [settings.USPS_ID, settings.UPS_ID, settings.FEDEX_ID],
        "package_types": ["package"],
    }
    # next, limit the service codes
    codes = (
        settings.INTL_REGULAR + settings.INTL_FAST + settings.INTL_EXPRESS
        if international
        else settings.REGULAR + settings.FAST + settings.EXPRESS
    )

    if basket.is_media() and not international:
        codes.append(settings.USPS_MEDIA_MAIL)
    shipment_dict["rate_options"].update({"service_codes": codes})

    logger.warning(f">>> RATE OPTIONS:\n{shipment_dict['rate_options']}")
    return shipment_dict


def get_rates(engine, shipment):
    response = engine.get_rates_from_shipment(shipment)
    err = response.get("rate_response").get("errors")
    res = response.get("rate_response").get("rates") or response.get(
        "rate_response"
    ).get("invalid_rates")

    if not res and err:
        error_msgs = []
        error_msgs.extend(e.get("message") for e in err)
        raise (Exception(error_msgs[1] or error_msgs[0]))
    return res


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
        serviceCode = it["serviceCode"]
        cost = it["shipmentCost"]
        choices.append(ShippingChoiceSS(serviceCode, cost))

    return choices


def shipping_choices_for_order(order: Order):
    shipment = make_shipment_for_order(order)
    try:
        get_rates_response = get_rates(shipengine, shipment)
        #logger.warning(f"Raw rates response:\n{get_rates_response}")
        choices = list(map(lambda r: rate_to_choice(r), get_rates_response))
        #logger.warning(f"GET_RATES RETURNED {len(choices)} choices:\n{choices}")
        return choices
    except ShipEngineError as err:
        logger.error("==== ERROR calling ShipEngine")
        logger.error(err.to_json())
        return []


# shipping choice for basket
def shipping_choices_SE(basket: Basket, address_d: dict):
    shipment = make_SE_shipment(basket, address_d)

    try:
        get_rates_response = get_rates(shipengine, shipment)
        # logger.warning(f"GET_RATES RETURNED\n{get_rates_response}")
        return list(map(lambda r: rate_to_choice(r), get_rates_response))
    except ShipEngineError as err:
        logger.error("==== ERROR calling ShipEngine")
        logger.error(err.to_json())
        return []


# SE rates inside a response:
HARDCODED_SE_RATES = [
    {
        "rate_id": "se-6031769783",
        "rate_type": "shipment",
        "carrier_id": "se-660216",
        "shipping_amount": {"currency": "usd", "amount": 104.58},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 16.21},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Shipping",
                "carrier_billing_code": "BaseServiceCharge",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 104.58},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "Fuel Surcharge",
                "carrier_billing_code": "375",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 16.21},
                "billing_source": "Carrier",
            },
        ],
        "zone": None,
        "package_type": None,
        "delivery_days": 1,
        "guaranteed_service": True,
        "estimated_delivery_date": "2024-10-15T10:30:00Z",
        "carrier_delivery_days": "Tuesday 10/15 by 10:30 AM",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "UPS Next Day Air®",
        "service_code": "ups_next_day_air",
        "trackable": True,
        "carrier_code": "ups",
        "carrier_nickname": "ShipEngine Test Account - UPS",
        "carrier_friendly_name": "UPS",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769784",
        "rate_type": "shipment",
        "carrier_id": "se-660216",
        "shipping_amount": {"currency": "usd", "amount": 134.58},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 20.86},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Shipping",
                "carrier_billing_code": "BaseServiceCharge",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 134.58},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "Fuel Surcharge",
                "carrier_billing_code": "375",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 20.86},
                "billing_source": "Carrier",
            },
        ],
        "zone": None,
        "package_type": None,
        "delivery_days": 1,
        "guaranteed_service": True,
        "estimated_delivery_date": "2024-10-15T08:00:00Z",
        "carrier_delivery_days": "Tuesday 10/15 by 08:00 AM",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "UPS Next Day Air® Early",
        "service_code": "ups_next_day_air_early_am",
        "trackable": True,
        "carrier_code": "ups",
        "carrier_nickname": "ShipEngine Test Account - UPS",
        "carrier_friendly_name": "UPS",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769785",
        "rate_type": "shipment",
        "carrier_id": "se-660216",
        "shipping_amount": {"currency": "usd", "amount": 91.81},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 14.23},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Shipping",
                "carrier_billing_code": "BaseServiceCharge",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 91.81},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "Fuel Surcharge",
                "carrier_billing_code": "375",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 14.23},
                "billing_source": "Carrier",
            },
        ],
        "zone": None,
        "package_type": None,
        "delivery_days": 1,
        "guaranteed_service": True,
        "estimated_delivery_date": "2024-10-15T23:00:00Z",
        "carrier_delivery_days": "Tuesday 10/15 by 11:00 PM",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "UPS Next Day Air Saver®",
        "service_code": "ups_next_day_air_saver",
        "trackable": True,
        "carrier_code": "ups",
        "carrier_nickname": "ShipEngine Test Account - UPS",
        "carrier_friendly_name": "UPS",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769786",
        "rate_type": "shipment",
        "carrier_id": "se-660216",
        "shipping_amount": {"currency": "usd", "amount": 40.92},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 6.34},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Shipping",
                "carrier_billing_code": "BaseServiceCharge",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 40.92},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "Fuel Surcharge",
                "carrier_billing_code": "375",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 6.34},
                "billing_source": "Carrier",
            },
        ],
        "zone": None,
        "package_type": None,
        "delivery_days": 2,
        "guaranteed_service": True,
        "estimated_delivery_date": "2024-10-16T23:00:00Z",
        "carrier_delivery_days": "Wednesday 10/16 by 11:00 PM",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "UPS 2nd Day Air®",
        "service_code": "ups_2nd_day_air",
        "trackable": True,
        "carrier_code": "ups",
        "carrier_nickname": "ShipEngine Test Account - UPS",
        "carrier_friendly_name": "UPS",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769787",
        "rate_type": "shipment",
        "carrier_id": "se-660216",
        "shipping_amount": {"currency": "usd", "amount": 47.77},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 7.4},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Shipping",
                "carrier_billing_code": "BaseServiceCharge",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 47.77},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "Fuel Surcharge",
                "carrier_billing_code": "375",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 7.4},
                "billing_source": "Carrier",
            },
        ],
        "zone": None,
        "package_type": None,
        "delivery_days": 2,
        "guaranteed_service": True,
        "estimated_delivery_date": "2024-10-16T10:30:00Z",
        "carrier_delivery_days": "Wednesday 10/16 by 10:30 AM",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "UPS 2nd Day Air AM®",
        "service_code": "ups_2nd_day_air_am",
        "trackable": True,
        "carrier_code": "ups",
        "carrier_nickname": "ShipEngine Test Account - UPS",
        "carrier_friendly_name": "UPS",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769788",
        "rate_type": "shipment",
        "carrier_id": "se-660216",
        "shipping_amount": {"currency": "usd", "amount": 35.96},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 5.57},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Shipping",
                "carrier_billing_code": "BaseServiceCharge",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 35.96},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "Fuel Surcharge",
                "carrier_billing_code": "375",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 5.57},
                "billing_source": "Carrier",
            },
        ],
        "zone": None,
        "package_type": None,
        "delivery_days": 3,
        "guaranteed_service": True,
        "estimated_delivery_date": "2024-10-17T23:00:00Z",
        "carrier_delivery_days": "Thursday 10/17 by 11:00 PM",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "UPS 3 Day Select®",
        "service_code": "ups_3_day_select",
        "trackable": True,
        "carrier_code": "ups",
        "carrier_nickname": "ShipEngine Test Account - UPS",
        "carrier_friendly_name": "UPS",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769789",
        "rate_type": "shipment",
        "carrier_id": "se-660216",
        "shipping_amount": {"currency": "usd", "amount": 13.38},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 2.21},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Shipping",
                "carrier_billing_code": "BaseServiceCharge",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 13.38},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "Fuel Surcharge",
                "carrier_billing_code": "375",
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 2.21},
                "billing_source": "Carrier",
            },
        ],
        "zone": None,
        "package_type": None,
        "delivery_days": 4,
        "guaranteed_service": True,
        "estimated_delivery_date": "2024-10-18T23:00:00Z",
        "carrier_delivery_days": "Friday 10/18 by 11:00 PM",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "UPS® Ground",
        "service_code": "ups_ground",
        "trackable": True,
        "carrier_code": "ups",
        "carrier_nickname": "ShipEngine Test Account - UPS",
        "carrier_friendly_name": "UPS",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769790",
        "rate_type": "shipment",
        "carrier_id": "se-660217",
        "shipping_amount": {"currency": "usd", "amount": 134.54},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 7.67},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "uncategorized",
                "carrier_description": "Demand Surcharge",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 0.9},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "Fuel",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 6.77},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Total Net Freight",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 134.54},
                "billing_source": "Carrier",
            },
        ],
        "zone": 8,
        "package_type": None,
        "delivery_days": 1,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-15T08:00:00Z",
        "carrier_delivery_days": "Tuesday 10/15 by 08:00 AM",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "FedEx First Overnight®",
        "service_code": "fedex_first_overnight",
        "trackable": True,
        "carrier_code": "fedex",
        "carrier_nickname": "ShipEngine Test Account - FedEx",
        "carrier_friendly_name": "FedEx",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769791",
        "rate_type": "shipment",
        "carrier_id": "se-660217",
        "shipping_amount": {"currency": "usd", "amount": 103.54},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 6.12},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "uncategorized",
                "carrier_description": "Demand Surcharge",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 0.9},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "Fuel",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 5.22},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Total Net Freight",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 103.54},
                "billing_source": "Carrier",
            },
        ],
        "zone": 8,
        "package_type": None,
        "delivery_days": 1,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-15T10:30:00Z",
        "carrier_delivery_days": "Tuesday 10/15 by 10:30 AM",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "FedEx Priority Overnight®",
        "service_code": "fedex_priority_overnight",
        "trackable": True,
        "carrier_code": "fedex",
        "carrier_nickname": "ShipEngine Test Account - FedEx",
        "carrier_friendly_name": "FedEx",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769792",
        "rate_type": "shipment",
        "carrier_id": "se-660217",
        "shipping_amount": {"currency": "usd", "amount": 90.89},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 5.49},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "uncategorized",
                "carrier_description": "Demand Surcharge",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 0.9},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "Fuel",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 4.59},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Total Net Freight",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 90.89},
                "billing_source": "Carrier",
            },
        ],
        "zone": 8,
        "package_type": None,
        "delivery_days": 1,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-15T17:00:00Z",
        "carrier_delivery_days": "Tuesday 10/15 by 05:00 PM",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "FedEx Standard Overnight®",
        "service_code": "fedex_standard_overnight",
        "trackable": True,
        "carrier_code": "fedex",
        "carrier_nickname": "ShipEngine Test Account - FedEx",
        "carrier_friendly_name": "FedEx",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769793",
        "rate_type": "shipment",
        "carrier_id": "se-660217",
        "shipping_amount": {"currency": "usd", "amount": 47.88},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 3.34},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "uncategorized",
                "carrier_description": "Demand Surcharge",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 0.9},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "Fuel",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 2.44},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Total Net Freight",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 47.88},
                "billing_source": "Carrier",
            },
        ],
        "zone": 8,
        "package_type": None,
        "delivery_days": 2,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-16T10:30:00Z",
        "carrier_delivery_days": "Wednesday 10/16 by 10:30 AM",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "FedEx 2Day® A.M.",
        "service_code": "fedex_2day_am",
        "trackable": True,
        "carrier_code": "fedex",
        "carrier_nickname": "ShipEngine Test Account - FedEx",
        "carrier_friendly_name": "FedEx",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769794",
        "rate_type": "shipment",
        "carrier_id": "se-660217",
        "shipping_amount": {"currency": "usd", "amount": 40.51},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 2.97},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "uncategorized",
                "carrier_description": "Demand Surcharge",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 0.9},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "Fuel",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 2.07},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Total Net Freight",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 40.51},
                "billing_source": "Carrier",
            },
        ],
        "zone": 8,
        "package_type": None,
        "delivery_days": 2,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-16T17:00:00Z",
        "carrier_delivery_days": "Wednesday 10/16 by 05:00 PM",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "FedEx 2Day®",
        "service_code": "fedex_2day",
        "trackable": True,
        "carrier_code": "fedex",
        "carrier_nickname": "ShipEngine Test Account - FedEx",
        "carrier_friendly_name": "FedEx",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769795",
        "rate_type": "shipment",
        "carrier_id": "se-660217",
        "shipping_amount": {"currency": "usd", "amount": 37.08},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 2.8},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "uncategorized",
                "carrier_description": "Demand Surcharge",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 0.9},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "Fuel",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 1.9},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Total Net Freight",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 37.08},
                "billing_source": "Carrier",
            },
        ],
        "zone": 8,
        "package_type": None,
        "delivery_days": 3,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-17T17:00:00Z",
        "carrier_delivery_days": "Thursday 10/17 by 05:00 PM",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "FedEx Express Saver®",
        "service_code": "fedex_express_saver",
        "trackable": True,
        "carrier_code": "fedex",
        "carrier_nickname": "ShipEngine Test Account - FedEx",
        "carrier_friendly_name": "FedEx",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769796",
        "rate_type": "shipment",
        "carrier_id": "se-660217",
        "shipping_amount": {"currency": "usd", "amount": 13.38},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.74},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "FedEx Ground Fuel",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 0.74},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Total Net Freight",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 13.38},
                "billing_source": "Carrier",
            },
        ],
        "zone": 8,
        "package_type": None,
        "delivery_days": 5,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-21T23:59:00Z",
        "carrier_delivery_days": "5",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "FedEx Ground®",
        "service_code": "fedex_ground",
        "trackable": True,
        "carrier_code": "fedex",
        "carrier_nickname": "ShipEngine Test Account - FedEx",
        "carrier_friendly_name": "FedEx",
        "validation_status": "has_warnings",
        "warning_messages": [
            "FedEx may add a Home Delivery Surcharge to this shipment later if this is a residential address."
        ],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769797",
        "rate_type": "shipment",
        "carrier_id": "se-660217",
        "shipping_amount": {"currency": "usd", "amount": 13.38},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 7.12},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "delivery",
                "carrier_description": "Residential delivery surcharge",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 5.55},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "uncategorized",
                "carrier_description": "Demand Surcharge",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 0.5},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "fuel_charge",
                "carrier_description": "FedEx Ground Fuel",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 1.07},
                "billing_source": "Carrier",
            },
            {
                "rate_detail_type": "shipping",
                "carrier_description": "Total Net Freight",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 13.38},
                "billing_source": "Carrier",
            },
        ],
        "zone": 8,
        "package_type": None,
        "delivery_days": 5,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-21T23:59:00Z",
        "carrier_delivery_days": "5",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "FedEx Home Delivery®",
        "service_code": "fedex_home_delivery",
        "trackable": True,
        "carrier_code": "fedex",
        "carrier_nickname": "ShipEngine Test Account - FedEx",
        "carrier_friendly_name": "FedEx",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769798",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 3.15},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 3.15},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "large_envelope_or_flat",
        "delivery_days": 5,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-21T00:00:00Z",
        "carrier_delivery_days": "5",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS First Class Mail",
        "service_code": "usps_first_class_mail",
        "trackable": False,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769799",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 5.03},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 5.03},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "package",
        "delivery_days": 5,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-21T00:00:00Z",
        "carrier_delivery_days": "5",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS First Class Mail",
        "service_code": "usps_first_class_mail",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769800",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 11.29},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 11.29},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "package",
        "delivery_days": 2,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-17T00:00:00Z",
        "carrier_delivery_days": "2",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Priority Mail",
        "service_code": "usps_priority_mail",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769801",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 16.85},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 16.85},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "medium_flat_rate_box",
        "delivery_days": 2,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-17T00:00:00Z",
        "carrier_delivery_days": "2",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Priority Mail",
        "service_code": "usps_priority_mail",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769802",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 9.55},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 9.55},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "small_flat_rate_box",
        "delivery_days": 2,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-17T00:00:00Z",
        "carrier_delivery_days": "2",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Priority Mail",
        "service_code": "usps_priority_mail",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769803",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 23.05},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 23.05},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "large_flat_rate_box",
        "delivery_days": 2,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-17T00:00:00Z",
        "carrier_delivery_days": "2",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Priority Mail",
        "service_code": "usps_priority_mail",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769804",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 9.0},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 9.0},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "flat_rate_envelope",
        "delivery_days": 2,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-17T00:00:00Z",
        "carrier_delivery_days": "2",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Priority Mail",
        "service_code": "usps_priority_mail",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769805",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 9.8},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 9.8},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "flat_rate_padded_envelope",
        "delivery_days": 2,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-17T00:00:00Z",
        "carrier_delivery_days": "2",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Priority Mail",
        "service_code": "usps_priority_mail",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769806",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 9.3},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 9.3},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "flat_rate_legal_envelope",
        "delivery_days": 2,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-17T00:00:00Z",
        "carrier_delivery_days": "2",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Priority Mail",
        "service_code": "usps_priority_mail",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769807",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 42.1},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 42.1},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "package",
        "delivery_days": 2,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-17T00:00:00Z",
        "carrier_delivery_days": "2",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Priority Mail Express",
        "service_code": "usps_priority_mail_express",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769808",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 27.9},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 27.9},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "flat_rate_envelope",
        "delivery_days": 2,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-17T00:00:00Z",
        "carrier_delivery_days": "2",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Priority Mail Express",
        "service_code": "usps_priority_mail_express",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769809",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 28.4},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 28.4},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "flat_rate_padded_envelope",
        "delivery_days": 2,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-17T00:00:00Z",
        "carrier_delivery_days": "2",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Priority Mail Express",
        "service_code": "usps_priority_mail_express",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769810",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 28.2},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 28.2},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "flat_rate_legal_envelope",
        "delivery_days": 2,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-17T00:00:00Z",
        "carrier_delivery_days": "2",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Priority Mail Express",
        "service_code": "usps_priority_mail_express",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769811",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 4.63},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 4.63},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "package",
        "delivery_days": 7,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-23T00:00:00Z",
        "carrier_delivery_days": "7",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Media Mail",
        "service_code": "usps_media_mail",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769812",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 5.03},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 5.03},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "package",
        "delivery_days": 5,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-21T00:00:00Z",
        "carrier_delivery_days": "5",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Parcel Select Ground",
        "service_code": "usps_parcel_select",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
    {
        "rate_id": "se-6031769813",
        "rate_type": "shipment",
        "carrier_id": "se-660215",
        "shipping_amount": {"currency": "usd", "amount": 5.03},
        "insurance_amount": {"currency": "usd", "amount": 0.0},
        "confirmation_amount": {"currency": "usd", "amount": 0.0},
        "other_amount": {"currency": "usd", "amount": 0.0},
        "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
        "rate_details": [
            {
                "rate_detail_type": "shipping",
                "carrier_description": "shipping",
                "carrier_billing_code": None,
                "carrier_memo": None,
                "amount": {"currency": "usd", "amount": 5.03},
                "billing_source": "Carrier",
            }
        ],
        "zone": 8,
        "package_type": "package",
        "delivery_days": 5,
        "guaranteed_service": False,
        "estimated_delivery_date": "2024-10-21T00:00:00Z",
        "carrier_delivery_days": "5",
        "ship_date": "2024-10-14T00:00:00Z",
        "negotiated_rate": False,
        "service_type": "USPS Ground Advantage",
        "service_code": "usps_ground_advantage",
        "trackable": True,
        "carrier_code": "stamps_com",
        "carrier_nickname": "ShipEngine Test Account - Stamps.com",
        "carrier_friendly_name": "Stamps.com",
        "validation_status": "valid",
        "warning_messages": [],
        "error_messages": [],
    },
]
