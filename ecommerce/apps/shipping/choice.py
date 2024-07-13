import json
from datetime import datetime
from json import JSONEncoder

from django.conf import settings

# from rest_framework import serializers


class ShippingChoice:
    def __lt__(self, other):
        return self.price < other.price

    def __init__(self, name, price, id, days):
        self.name = name
        self.price = price
        self.id = id
        self.days = days

    def __eq__(self, other):
        if isinstance(other, ShippingChoice):
            return (
                self.name == other.name
                and self.id == other.id
                and self.price == other.price
                and self.days == other.days
            )
        return False

    def from_repr(it):
        [name, price, id, days] = it.split("/")
        return ShippingChoice(name, float(price), id, int(days))

    # basket_update_delivery relies on this format!

    def __repr__(self):
        return f"{self.name}/{self.price}/{self.id}/{self.days}"


def rate_to_choice(rate_d):
    # print(f"rate_d:{rate_d}")
    print("###############")
    return ShippingChoice(
        rate_d.get("service_code"),
        rate_d.get("shipping_amount").get("amount"),
        rate_d.get("rate_id"),
        rate_d.get("delivery_days"),
    )


def split_tiers(choices):
    reg = [x for x in choices if x.name in settings.REGULAR]
    exp = [x for x in choices if x.name in settings.EXPEDITED]
    fas = [x for x in choices if x.name in settings.FAST]

    return {"regular": reg, "express": exp, "fast": fas}


# {
#     "rate_id": "se-5534654739",
#     "rate_type": "shipment",
#     "carrier_id": "se-660217",
#     "shipping_amount": {"currency": "usd", "amount": 15.64},
#     "insurance_amount": {"currency": "usd", "amount": 0.0},
#     "confirmation_amount": {"currency": "usd", "amount": 0.0},
#     "other_amount": {"currency": "usd", "amount": 0.86},
#     "requested_comparison_amount": {"currency": "usd", "amount": 0.0},
#     "rate_details": [
#         {
#             "rate_detail_type": "fuel_charge",
#             "carrier_description": "FedEx Ground Fuel",
#             "carrier_billing_code": None,
#             "carrier_memo": None,
#             "amount": {"currency": "usd", "amount": 0.86},
#         },
#         {
#             "rate_detail_type": "shipping",
#             "carrier_description": "Total Net Freight",
#             "carrier_billing_code": None,
#             "carrier_memo": None,
#             "amount": {"currency": "usd", "amount": 15.64},
#         },
#     ],
#     "zone": 8,
#     "package_type": "package",
#     "delivery_days": 5,
#     "guaranteed_service": False,
#     "estimated_delivery_date": "2024-07-03T23:59:00Z",
#     "carrier_delivery_days": "5",
#     "ship_date": "2024-06-26T00:00:00Z",
#     "negotiated_rate": False,
#     "service_type": "FedEx Ground®", # or this !!!!
#     "service_code": "fedex_ground",
#     "trackable": True,
#     "carrier_code": "fedex",
#     "carrier_nickname": "ShipEngine Test Account - FedEx",
#     "carrier_friendly_name": "FedEx", # this may be necessary to display!!!
#     "validation_status": "has_warnings",
#     "warning_messages": [
#         "FedEx may add a Home Delivery Surcharge to this shipment later if this is a residential address."
#     ],
#     "error_messages": [],
# }
