import factory

from faker import Faker
from ecommerce.apps.catalogue.models import Product

from ecommerce.apps.inventory.models import ProductInventory, ProductType, Room, Stock

fake = Faker()


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    name = "Room_from_factory"


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    title = "Product_from_factory"


class ProductTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductType

    name = "ProductType_from_factory"


class ProductInvFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductInventory

    product = factory.SubFactory(ProductFactory)
    product_type = factory.SubFactory(ProductTypeFactory)
    sku = "F-99"
    target_amount = 10
    weight = 11
    

class StockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Stock

    productinv = factory.SubFactory(ProductInvFactory)
    room = factory.SubFactory(RoomFactory)
    quantity = 7
    