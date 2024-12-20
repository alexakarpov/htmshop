from ecommerce.apps.orders.models import Order, OrderItem
from ecommerce.apps.inventory.models import Stock
from faker import Faker
from random import random, randint
from datetime import datetime

fake = Faker()


def make_order():
    o = Order()
    o.full_name = fake.name()
    o.address_line1 = fake.street_address()
    o.city_locality = fake.city()
    o.phone = fake.numerify("###-###-####")
    o.postal_code = fake.postalcode()
    o.state_province = fake.state()
    o.status = "PROCESSING"
    o.shipping_cost = 12.00
    o.shipping_method = "REGULAR"
    o.email = fake.email()
    od_str = input("when was it placed (YYYY-MM-DD)? ")
    o.created_at = datetime.strptime(od_str, "%Y-%m-%d")
    sku = input("which SKU? ")
    st = Stock.objects.get(sku=sku)
    qty_s = input("quantity? ")
    qty_i = int(qty_s)
    o.subtotal = qty_i * st.price
    o.save()
    oi = OrderItem()
    oi.order = o

    oi.stock = st
    oi.sku = st.sku

    oi.quantity = qty_i
    oi.price = qty_i * st.price

    oi.title = st.product.title
    oi.save()
    o.items.add(oi)
    o.save()

    return o


def run():
    s_n_orders = input("how many orders? ")
    N_ORDERS = int(s_n_orders)

    for n in range(1, N_ORDERS + 1):
        o = make_order()
        print(f"generated order #{n}")
