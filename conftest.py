pytest_plugins = [
    "ecommerce.tests.fixtures",
    "ecommerce.tests.factories",
]

import pytest
from pytest_factoryboy import register
from ecommerce.tests.factories import RoomFactory, StockFactory

register(RoomFactory)
register(StockFactory)