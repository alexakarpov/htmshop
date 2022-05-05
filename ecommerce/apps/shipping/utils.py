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
    print(f">>> {basket}")
    total = 0
    for (k, v) in basket.items():
        print(f"k is: {k}({type(k)})")
        print(f"v is: {v}({type(v)})")

        w = v["weight"]
        q = v["qty"]
        total += w * q

    # {'price': Decimal('30.00'),
    #  'qty': 2,
    #  'variant': '8x10',
    #  'title': 'Holy Napkin',
    #  'product': <Product: Holy Napkin>,
    #  'total_price': Decimal('60.00')}

    return total
