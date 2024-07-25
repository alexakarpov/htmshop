from ecommerce.constants import BOOKSTORE_DISCOUNT_A


def discount(item):
    if item.stock.sku[0] == "A":
        return item.price - item.stock.percentage(BOOKSTORE_DISCOUNT_A)
    else:
        return item.price
