from django.conf import settings
from decimal import Decimal
# from rest_framework import serializers


class ShippingChoiceSE:
    def __lt__(self, other):
        return self.price < other.price

    def __init__(self, name, price, id, days):
        self.name = name
        self.price = price
        self.id = id
        self.days = days

    def __eq__(self, other):
        if isinstance(other, ShippingChoiceSE):
            return (
                self.name == other.name
                and self.id == other.id
                and self.price == other.price
                and self.days == other.days
            )
        return False

    def from_repr(it):
        [name, price, id, days] = it.split("/")
        return ShippingChoiceSE(name, Decimal(price), id, int(days))

    # basket_update_delivery relies on this format!

    def __repr__(self):
        return f"{self.name}/{self.price}/{self.id}/{self.days}"


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

    def from_repr(it):
        [serviceCode, price, name] = it.split("/")
        return ShippingChoiceSS(serviceCode, float(price), name)

    # basket_update_delivery relies on this format!

    def __repr__(self):
        return f"{self.serviceCode}/{self.price}"


def rate_to_choice(rate_d):
    return ShippingChoiceSE(
        rate_d.get("service_code"),
        rate_d.get("shipping_amount").get("amount"),
        rate_d.get("rate_id"),
        rate_d.get("delivery_days"),
    )


def split_tiers_SE(choices, international=False):
    if international:
        regular = [x for x in choices if x.name in settings.INTL_REGULAR]
        express = [x for x in choices if x.name in settings.INTL_EXPRESS]
        fast = [x for x in choices if x.name in settings.INTL_FAST]
    else:
        regular = [x for x in choices if x.name in settings.REGULAR]
        express = [x for x in choices if x.name in settings.EXPRESS]
        fast = [x for x in choices if x.name in settings.FAST]

    return {"regular": regular, "express": express, "fast": fast}


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
