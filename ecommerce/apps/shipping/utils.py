from pint import UnitRegistry

ureg = UnitRegistry()


def variants(product_type):
    if product_type.name == "icons":
        return ["8x10", "wallet-size"]
    elif product_type.name == "incense":
        return ["1 lb", "1/2 lb", "1 oz"]
    else:
        return []


def get_weight(basket):
    print(basket)
    total = 0
    for it in basket:
        ## key is the product id, v is the 'basket item' dict
        # with all the metadata
        # print(f"k is: {k}({type(k)})")
        # print(f"v is: {v}({type(v)})")

        w = it["weight"]
        q = it["qty"]
        total += w * q

    return total
