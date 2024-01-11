from django import template
from ecommerce.apps.accounts.models import Account
from ecommerce.apps.inventory.models import Stock
from ecommerce.constants import (
    ANGEL_EMAILS,
    BOOKSTORE_DISCOUNT_A,
    BOOKSTORE_DISCOUNT_ARCHANGELS,
    BOOKSTORE_DISCOUNT_I,
)

register = template.Library()


@register.simple_tag
def display_price(customer: Account, stock: Stock):
    verdict = ""
    if (
        customer.is_anonymous
        or not customer.is_bookstore
        or stock.is_enlargement()
        or stock.is_print()
    ):
        verdict = f"{stock.price}"  # discounts not applicable
    else:
        if stock.is_aseries():
            if customer.email in ANGEL_EMAILS:
                verdict = f"{stock.price - stock.percentage(BOOKSTORE_DISCOUNT_ARCHANGELS)} ( ${stock.price} )"
            else: # regular bookstore
                verdict = f"{stock.price - stock.percentage(BOOKSTORE_DISCOUNT_A)} ( ${stock.price} )"
        elif stock.is_our_book():
            verdict = f"{stock.price - stock.percentage(BOOKSTORE_DISCOUNT_A)} ( ${stock.price} )"
        if stock.is_incense():
            verdict = f"{stock.price - stock.percentage(BOOKSTORE_DISCOUNT_I)} ( ${stock.price} )"
        if verdict == "":
            verdict = f"{stock.price}"  # no discounts on the stock
        
    return verdict


@register.simple_tag
def get_price(customer: Account, stock: Stock):
    if (
        customer.is_anonymous
        or not customer.is_bookstore
        or stock.is_enlargement()
        or stock.is_print()
    ):
        return stock.price
    else:
        if (
            customer.email in ANGEL_EMAILS
            and stock.is_aseries()
            and not stock.is_print()
            and not stock.is_enlargement()
        ):
            return stock.price - stock.percentage(BOOKSTORE_DISCOUNT_ARCHANGELS)
        if (
            stock.is_aseries() and not stock.is_enlargement()
        ) or stock.is_our_book():
            return stock.price - stock.percentage(BOOKSTORE_DISCOUNT_A)
        if stock.is_incense():
            return stock.price - stock.percentage(BOOKSTORE_DISCOUNT_I)
        return stock.price
