# pytest will pick up these fixtures automatically as per conftest.py


import pytest

from ecommerce.apps.inventory.models import Stock
# from django.core.management import call_command

@pytest.fixture(scope='session')
def sku_a9():
    print("running sku_a9 fixture")
    return "A-9"

@pytest.fixture()
def make_stock(db, stock_factory):
    stock = stock_factory.build()
    return stock