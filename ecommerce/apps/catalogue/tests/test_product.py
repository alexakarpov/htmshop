from django.test import TestCase

from ecommerce.apps.catalogue.models import (
    Product,
)
from ecommerce.apps.inventory.models import (
    ProductInventory,
    ProductType,
)

from ecommerce.constants import *


class ProductTest(TestCase):
    fixtures = [
        "catalogue.json",
        "inventory.json",
    ]

    def test_type_name(self):
        books = ProductType.objects.get(name="book")
        self.assertEqual(books.name, PRODUCT_TYPE_BOOK)

    def test_product_get_skus(self):
        """
        a 'variant' is really a specific SKU for a product
        e,g, for a book there's a single SKU/variant,
        but mounted icons can have many
        """
        book_p = Product.objects.get(slug=TEST_BOOK_SLUG)
        icon_p = Product.objects.get(slug=TEST_ICON2_SLUG)
        i_skus = icon_p.get_skus()
        b_skus = book_p.get_skus()
        self.assertEqual(
            b_skus.count(),
            1,
            "fixture contains a single variant of Psalter",
        )
        self.assertEqual(
            len(i_skus), 2, "fixture has 2 variants of the Unburning Bush"
        )
        icon_v1 = i_skus[0]
        self.assertIsInstance(icon_v1, ProductInventory)
