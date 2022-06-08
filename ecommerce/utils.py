from pint import UnitRegistry

ureg = UnitRegistry()


def variants(product_type):
    if product_type.name == "icons":
        return ["8x10", "wallet-size"]
    elif product_type.name == "incense":
        return ["1 lb", "1/2 lb", "1 oz"]
    else:
        return []

def debug_print(it):
    print("========")
    print(it)
    print("^^^^^^^^")

def get_weight(basket_ds):
    print(f"basket_ds: {basket_ds}")
    total = 0
    for it in basket_ds:
        w = it["weight"]
        q = it["qty"]
        total += w * q

    return total
