from pint import UnitRegistry

ureg = UnitRegistry()


def variants(product_type):
    if product_type.name == "mounted_icon":
        return ["8x10", "wallet-size"]
    elif product_type.name == "incense":
        return ["1 lb", "1/2 lb", "1 oz"]
    else:
        return []
