import factory
from ecommerce.apps.accounts.models import Account, Address
from ecommerce.apps.catalogue.models import (
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductType,
)
from faker import Faker

fake = Faker()

####
# Catalogue
####


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = "django"
    slug = "django"


class ProductTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductType
        django_get_or_create = ("name",)

    name = "book"


class ProductAttributeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductAttribute

    product_type = factory.SubFactory(ProductTypeFactory)
    name = "pages"


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    product_type = factory.SubFactory(ProductTypeFactory)
    category = factory.SubFactory(CategoryFactory)
    title = "product_title"
    description = fake.text()
    slug = "product_slug"
    price = "9.99"


class ProductAttributeValueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductAttributeValue

    product = factory.SubFactory(ProductFactory)
    attribute = factory.SubFactory(ProductAttributeFactory)
    value = "100"


####
# Account
####


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    email = "a@a.com"
    phone = "07525251252"
    password = "tester"
    is_active = True
    is_staff = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        if "is_superuser" in kwargs:
            return manager.create_superuser(*args, **kwargs)
        else:
            return manager.create_user(*args, **kwargs)


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    customer = factory.SubFactory(AccountFactory)
    full_name = fake.name()
    phone = fake.phone_number()
    postcode = fake.postcode()
    address_line = fake.street_address()
    address_line2 = fake.street_address()
    town_city = fake.city_suffix()
