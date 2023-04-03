import factory

from faker import Faker
from ecommerce.apps.catalogue.models import Product

from ecommerce.apps.inventory.models import ProductStock, ProductType

fake = Faker()


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    title = "Product_from_factory"


class ProductTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductType

    name = "ProductType_from_factory"


class ProductStockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductStock

    product = factory.SubFactory(ProductFactory)
    product_type = factory.SubFactory(ProductTypeFactory)
    sku = "F-99"
    target_amount = 10
    weight = 11
