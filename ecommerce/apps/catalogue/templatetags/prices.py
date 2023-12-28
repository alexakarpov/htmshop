from django import template
from ecommerce.apps.accounts.models import Account
from ecommerce.apps.inventory.models import Stock

register = template.Library()

@register.simple_tag
def get_price(customer: Account, stock: Stock):
    if customer.is_bookstore:
        if stock.is_aseries() and stock.sku.find('x') == -1:
            return stock.price - stock.percentage(30)
        if stock.is_incense():
            return stock.price - stock.percentage(15)
    return stock.price
