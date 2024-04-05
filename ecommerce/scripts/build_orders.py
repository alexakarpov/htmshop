from ecommerce.apps.orders.models import Order, OrderItem
from ecommerce.apps.inventory.models import Stock
from faker import Faker
from random import random, randint

fake = Faker()


def run():

    N_ORDERS = randint(10,50)
    print(f"generating {N_ORDERS} random orders")

    icons = Stock.objects.filter(sku__startswith='A-').exclude(sku__contains='x')
    N_A_SERIES = icons.count() 
    print(f"got {N_A_SERIES} basic icon stocks")
    for n in range(1, N_ORDERS):
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
        oi.quantity = randint(1,5)
        st = oi.stock = icons[randint(0,N_A_SERIES)]
        oi.price = 32.0
        oi.title = st.product.title
        o.save()
        oi.save()

        print(f'generatin order #{n}... -> {o.pk}')

