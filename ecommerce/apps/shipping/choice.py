import json
from datetime import datetime
from json import JSONEncoder

from django.conf import settings

# from rest_framework import serializers


class ShippingChoice():
    def __lt__(self, other):
        return self.price < other.price

    def __init__(self, name, price, id, days):
        self.name = name
        self.price = price
        self.id = id
        self.days = days

    def __eq__(self, other):
        if isinstance(other, ShippingChoice):
            return self.name == other.name and self.id == other.id and self.price == other.price and self.days == other.days
        return False

    def from_repr(it):
        [name, price, id, days] = it.split('/')
        return ShippingChoice(name, float(price), id, int(days))

    # basket_update_delivery relies on this format!

    def __repr__(self):
        return f"{self.name}/{self.price}/{self.id}/{self.days}"


def rate_to_choice(rate_d):
    return ShippingChoice(
        rate_d.get("service_code"),
        rate_d.get("shipping_amount").get("amount"),
        rate_d.get("rate_id"),
        rate_d.get("delivery_days"))


def split_tiers(choices):
    reg = [x for x in choices if x.name in settings.REGULAR]
    exp = [x for x in choices if x.name in settings.EXPEDITED]
    fas = [x for x in choices if x.name in settings.FAST]

    return {"regular": reg, "express": exp, "fast": fas}
