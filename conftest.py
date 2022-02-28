import pytest
from django.core.management import call_command
from pytest_factoryboy import register
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from tests.factories import (
    AccountFactory,
    AddressFactory,
    CategoryFactory,
    ProductFactory,
    ProductSpecificationFactory,
    ProductSpecificationValueFactory,
    ProductTypeFactory,
)

register(CategoryFactory)
register(ProductTypeFactory)
register(ProductSpecificationFactory)
register(ProductFactory)
register(ProductSpecificationValueFactory)
register(AccountFactory)
register(AddressFactory)


@pytest.fixture
def create_admin_user(django_user_model):
    """
    Return admin user
    """
    return django_user_model.objects.create_superuser("admin@example.com", "password")


@pytest.fixture(scope="session")
def db_fixture_setup(django_db_setup, django_db_blocker):
    """
    Load DB data fixtures
    """
    with django_db_blocker.unblock():
        call_command("migrate")
        call_command("loaddata", "ecommerce/data_fixtures/accounts.json")
        call_command("loaddata", "ecommerce/data_fixtures/catalogue.json")
        call_command("loaddata", "ecommerce/data_fixtures/db_admin_fixture.json")


@pytest.fixture(scope="module")
def chrome_browser_instance(request):
    """
    Provide a selenium webdriver instance
    """
    options = Options()
    options.headless = False
    browser = webdriver.Chrome(options=options)
    yield browser
    browser.close()


@pytest.fixture
def product_category(db, category_factory):  # here db is the Database fixture
    category = category_factory.create()
    return category


@pytest.fixture
def dummy_fix():
    print("print inside a fixture (function defined in conftest and marked with @pytest.fixture)")
    return "dumbledore"


@pytest.fixture
def product_type(db, product_type_factory):
    product_type = product_type_factory.create()
    return product_type


@pytest.fixture
def product_specification(db, product_specification_factory):
    product_spec = product_specification_factory.create()
    return product_spec


@pytest.fixture
def product(db, product_factory):
    product = product_factory.create()
    return product


@pytest.fixture
def product_spec_value(db, product_specification_value_factory):
    product_spec_value = product_specification_value_factory.create()
    return product_spec_value


@pytest.fixture
def customer(db, account_factory):
    new_customer = account_factory.create()
    return new_customer


@pytest.fixture
def adminuser(db, account_factory):
    new_account = account_factory.create(name="admin_user", is_staff=True, is_superuser=True)
    return new_account


@pytest.fixture
def address(db, address_factory):
    new_address = address_factory.create()
    return new_address
