from django.conf import settings
from decimal import Decimal

# from rest_framework import serializers


class ShippingChoiceSE:
    def __lt__(self, other):
        return self.price < other.price

    def __init__(self, price, id, service_code, days):
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
        [price, id, service_code, days] = it.split("/")
        return ShippingChoiceSE(Decimal(price), id, int(days), service_code)

    # basket_update_delivery relies on this format!

    def __repr__(self):
        return f"{self.price}/{self.id}/{self.service_code}/{self.days}"


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
        rate_d.get("service_code"),
        rate_d.get("delivery_days"),
    )


def split_tiers(
    choices, international=False
) -> dict[str, list[ShippingChoiceSE]]:

    if not choices:
        return {}

    regular_tier = []
    fast_tier = []
    express_tier = []

    fast_codes = settings.FAST
    express_codes = settings.EXPRESS

    if international:
        fast_codes = settings.INTL_FAST
        express_codes = settings.INTL_EXPRESS

    for choice in choices:
        if choice.service_code in express_codes:
            express_tier.append(choice)
        elif choice.service_code in fast_codes:
            fast_tier.append(choice)
        else:  # regular
            regular_tier.append(choice)

    return {
        "regular": regular_tier,
        "fast": fast_tier,
        "express": express_tier,
    }
