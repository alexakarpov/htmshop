from django.test import TestCase

from ecommerce.apps.catalogue.models import (
    Product,
)
from ecommerce.apps.inventory import (
    ProductInventory,
    ProductType,
)

from ecommerce.constants import *


class ProductTest(TestCase):
    fixtures = [
        "catalogue.json",
    ]

    def test_fixture_worked(self):
        self.assertEquals(
            Product.objects.all().count(), 6, "fixture has 6 Productss"
        )

    # def test_product_types_and_specs(self):
    #     p1 = ProductInventory.objects.get(sku=BOOK_SKU)
    #     p2 = ProductInventory.objects.get(slug=BB_SKU)
    #     self.assertEqual(
    #         p1.title, "Psalter", "fixture works, products loaded"
    #     )

    #     book_type = p1.product_type
    #     icon_type = p2.product_type
    #     p1_specs = p1.product_type.productspecification_set.all()
    #     p2_specs = p2.product_type.productspecification_set.all()
    #     all_specs = ProductSpecification.objects.all()
    #     book_specs = all_specs.filter(product_type=book_type)
    #     icon_specs = all_specs.filter(product_type=icon_type)
    #     self.assertEquals(
    #         book_specs.count(), 0, "there should be no specs for books"
    #     )
    #     self.assertEquals(
    #         icon_specs.count(), 1, "there should be 1 spec for icons"
    #     )
    #     spec = icon_specs.first()  # cmon, this isn't testing
    #     self.assertIn(spec, p2_specs, "Book's spec is in books specs")

    def test_type_name(self):
        books = ProductType.objects.get(name="book")
        self.assertEquals(books.name, PRODUCT_TYPE_BOOK)

    def test_product_get_variants(self):
        """
        a 'variant' is really a specific SKU for a product
        e,g, for a book there's a single SKU/variant,
        but mounted icons can have many
        """
        book_p = Product.objects.get(slug=BOOK_SLUG)
        icon_p = Product.objects.get(slug=BB_SLUG)
        i_skus = icon_p.get_skus()
        b_skus = book_p.get_skus()
        self.assertEquals(
            len(b_skus),
            1,
            "fixture contains a single variant of Psalter",
        )
        self.assertEquals(
            len(i_skus), 3, "fixture has 3 variants of the Holy Napkin"
        )
        icon_v1 = i_skus[0]
        self.assertIsInstance(icon_v1, ProductInventory)
