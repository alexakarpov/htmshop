from ecommerce.tests.factories import ProductStockFactory
from pytest_factoryboy import register
import pytest
pytest_plugins = [
    "ecommerce.tests.fixtures",
    "ecommerce.tests.factories",
]


register(ProductStockFactory)
