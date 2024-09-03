from django.conf import settings

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
        return ShippingChoiceSE(name, float(price), id, int(days))

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
        return ShippingChoiceSS(serviceCode, float(price), name )

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


def split_tiers_SE(choices, intl=False):
    reg = [x for x in choices if x.name in settings.REGULAR]
    exp = [x for x in choices if x.name in settings.EXPRESS]
    fas = [x for x in choices if x.name in settings.FAST]

    return {"regular": reg, "express": exp, "fast": fas}

def split_tiers_SS(choices, intl=False):
    print(f"splitting tiers from {choices} for intl {intl}")
    if intl:
        reg = [x for x in choices if x.serviceCode in settings.INTL_REGULAR]
        exp = [x for x in choices if x.serviceCode in settings.INTL_EXPRESS]
        fas = [x for x in choices if x.serviceCode in settings.INTL_FAST]
    else:
        reg = [x for x in choices if x.serviceCode in settings.REGULAR]
        exp = [x for x in choices if x.serviceCode in settings.EXPRESS]
        fas = [x for x in choices if x.serviceCode in settings.FAST]

    return {"regular": reg, "express": exp, "fast": fas}
