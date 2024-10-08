from django.conf import settings
from decimal import Decimal

# from rest_framework import serializers


class ShippingChoiceSE:
    def __lt__(self, other):
        return self.price < other.price

    def __init__(self, price, id, days, service_code):
        self.price = price
        self.id = id
        self.days = days
        self.service_code = service_code

    def __eq__(self, other):
        if isinstance(other, ShippingChoiceSE):
            return (
                self.service_code == other.service_code
                and self.id == other.id
                and self.price == other.price
                and self.days == other.days
            )
        return False

    @staticmethod
    def from_repr(it):
        [price, id, days, service_code] = it.split("/")
        return ShippingChoiceSE(Decimal(price), id, int(days), service_code)

    # basket_update_delivery relies on this format!

    def __repr__(self):
        return f"{self.price}/{self.id}/{self.days}/{self.service_code}"


class ShippingChoiceSS:
    def __lt__(self, other):
        return self.price < other.price

    def __init__(self, serviceCode, price):
        self.serviceCode = serviceCode
        self.price = price

    def __eq__(self, other):
        if isinstance(other, ShippingChoiceSS):
            return (
                self.serviceCode == other.serviceCode
                and self.price == other.price
            )
        return False

    @staticmethod
    def from_repr(it):
        [serviceCode, price, name] = it.split("/")
        return ShippingChoiceSS(serviceCode, float(price), name)

    # basket_update_delivery relies on this format!

    def __repr__(self):
        return f"{self.serviceCode}/{self.price}"


def rate_to_choice(rate_d: dict):
    return ShippingChoiceSE(
        rate_d.get("shipping_amount").get("amount"),
        rate_d.get("rate_id"),
        rate_d.get("delivery_days"),
        rate_d.get("service_code"),
    )


def split_tiers_SE(
    choices, international=False
) -> dict[str, list[ShippingChoiceSE]]:

    if not choices:
        return {}

    regular_tier = []
    fast_tier = []
    express_tier = []

    regular_codes = settings.REGULAR
    fast_codes = settings.FAST

    if international:
        regular_codes = settings.INTL_REGULAR
        fast_codes = settings.INTL_FAST

    for choice in choices:
        if choice.service_code in regular_codes:
            regular_tier.append(choice)
        elif choice.service_code in fast_codes:
            fast_tier.append(choice)
        else:  # express
            express_tier.append(choice)

    return {
        "regular": regular_tier,
        "fast": fast_tier,
        "express": express_tier,
    }


def split_tiers_SS(choices, international=False):
    if international:
        regular = [
            x for x in choices if x.serviceCode in settings.INTL_REGULAR
        ]
        fast = [x for x in choices if x.serviceCode in settings.INTL_FAST]
        express = [
            x for x in choices if x.serviceCode in settings.INTL_EXPRESS
        ]
    else:
        regular = [x for x in choices if x.serviceCode in settings.REGULAR]
        fast = [x for x in choices if x.serviceCode in settings.FAST]
        express = [x for x in choices if x.serviceCode in settings.EXPRESS]

    return {"regular": regular, "express": express, "fast": fast}


{
    "regular": [
        "ups_standard_international/25.41/se - 5985783218/3",
        "usps_first_class_mail_international/16.46/se-5985783221 / 2",
        "globalpost_economy/13.04/se-5985783224/14",
    ],
    "express": [
        "ups_worldwide_express/116.56/se-5985783216/1",
        "ups_worldwide_express_plus/116.56/se-5985783219/1",
        "ups_worldwide_saver/112.07/se-5985783220/1",
    ],
    "fast": [
        "ups_worldwide_expedited/104.93/se-5985783217/2",
        "usps_priority_mail_international/40.91/se-5985783222/10",
        "usps_priority_mail_express_international/57.32/se-5985783223/5",
        "globalpost_priority/12.69/se-5985783225/10",
        "gp_plus/11.5/se-5985783226/5",
    ],
}
