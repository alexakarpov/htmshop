from django import template
from ecommerce.apps.accounts.models import Account
from ecommerce.apps.inventory.models import Stock
from ecommerce.constants import (
    ANGEL_EMAILS,
    BOOKSTORE_DISCOUNT_A,
    BOOKSTORE_DISCOUNT_AL,
    BOOKSTORE_DISCOUNT_I,
)

register = template.Library()


@register.simple_tag
def get_price(customer: Account, stock: Stock):
    if customer.is_anonymous or customer.is_bookstore == False:
        return stock.price
    if (
        customer.email in ANGEL_EMAILS
        and stock.is_aseries() # not a print
        and stock.sku.find("x") == -1 # standard size
    ):
        return stock.price - stock.percentage(BOOKSTORE_DISCOUNT_AL)
    if stock.is_aseries() and stock.sku.find("x") == -1:
        return stock.price - stock.percentage(BOOKSTORE_DISCOUNT_A)
    if stock.is_incense():
        return stock.price - stock.percentage(BOOKSTORE_DISCOUNT_I)
