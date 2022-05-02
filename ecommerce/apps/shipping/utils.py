from pint import UnitRegistry

ureg = UnitRegistry()


def variants(product_type):
    if product_type.name == "icons":
        return ["8x10", "wallet-size"]
    elif product_type.name == "incense":
        return ["1lb", "1/2 lb", "1 oz"]
    else:
        return []


def get_weight(basket):
    total = 0
    for it in basket:
        p = it["product"]
        q = it["qty"]
        total += p.weight * q

    ounces = ureg.ounce * total

    print(f"{ounces.to('pounds')}")
    # {'price': Decimal('30.00'),
    #  'qty': 2,
    #  'variant': '8x10',
    #  'title': 'Holy Napkin',
    #  'product': <Product: Holy Napkin>,
    #  'total_price': Decimal('60.00')}

    return total
