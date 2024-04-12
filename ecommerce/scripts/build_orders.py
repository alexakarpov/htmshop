from ecommerce.apps.orders.models import Order, OrderItem
from ecommerce.apps.inventory.models import Stock
from faker import Faker
from random import random, randint

fake = Faker()


def make_order_with():
    o = Order()
    o.full_name = fake.name()
    o.address_line1 = fake.street_address()
    o.city_locality = fake.city()
    o.phone = fake.numerify("###-###-####")
    o.postal_code = fake.postalcode()
    o.state_province = fake.state()
    o.order_total = o.total_paid = 32.0
    o.paid = True
    o.shipping_cost = 12.00

    oi = OrderItem()
    oi.order = o

    sku = input("which SKU? ")
    
    st = oi.stock = Stock.objects.get(sku=sku)
    qty_s = input("quantity? ")
    qty_i = int(qty_s)
    oi.quantity = qty_i
    oi.price = 32.0
    oi.title = st.product.title
    o.save()
    oi.save()
    
    return o


def make_order(icon_stocks):
    N_A_SERIES = icon_stocks.count()
    o = Order()
    o.full_name = fake.name()
    o.address_line1 = fake.street_address()
    o.city_locality = fake.city()
    o.phone = fake.numerify("###-###-####")
    o.postal_code = fake.postalcode()
    o.state_province = fake.state()
    o.order_total = o.total_paid = 32.0
    o.paid = True
    o.shipping_cost = 12.00

    oi = OrderItem()
    oi.order = o
    oi.quantity = randint(1, 5)
    st = oi.stock = icon_stocks[randint(0, N_A_SERIES)]
    oi.price = 32.0
    oi.title = st.product.title
    o.save()
    oi.save()
    return o


def run():

    s_n_orders = input('how many orders? ')
    N_ORDERS = int(s_n_orders)

    for n in range(1, N_ORDERS+1):
        o = make_order_with()
        print(f"generating order #{n}... -> {o.pk}")
        
