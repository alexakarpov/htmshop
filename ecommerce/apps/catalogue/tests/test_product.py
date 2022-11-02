from django.test import TestCase

from ecommerce.apps.catalogue.models import (Product, ProductInventory,
                                             ProductSpecification,
                                             ProductSpecificationValue,
                                             ProductType)


class ProductTest(TestCase):
    fixtures = ['catalogue.json', ]

    def test_fixture_worked(self):
        self.assertEquals(Product.objects.all().count(),
                          3,
                          "fixture has 3 Productss")

    def test_product_types_and_specs(self):
        p1 = Product.objects.get(slug="pb")
        p2 = Product.objects.get(slug="hn")
        self.assertEqual(p1.title,
                         "Prayer Book",
                         "fixture works, products loaded")

        book = p1.product_type
        icon = p2.product_type
        p1_specs = p1.product_type.productspecification_set.all()
        p2_specs = p2.product_type.productspecification_set.all()
        all_specs = ProductSpecification.objects.all()
        book_specs = all_specs.filter(product_type=book)
        icon_specs = all_specs.filter(product_type=icon)
        self.assertEquals(book_specs.count(),
                          0,
                          "there should be no specs for books")
        self.assertEquals(icon_specs.count(),
                          1,
                          "there should be 1 spec for icons")
        spec = icon_specs.first()  # cmon, this isn't testing
        self.assertIn(spec,
                      p2_specs,
                      "Book's spec is in books specs")

    def test_type_name(self):
        books = ProductType.objects.get(name='books')
        self.assertEquals(books.name, "books")

    def test_product_get_variants(self):
        """
        a 'variant' is really a specific SKU for a product
        e,g, for a book there's a single SKU/variant,
        but mounted icons can have many
        """
        book_p = Product.objects.get(slug="pb")
        icon_p = Product.objects.get(slug="hn")
        b_variants = book_p.get_variants()
        i_variants = icon_p.get_variants()
        self.assertEquals(len(b_variants),
                          1,
                          "fixture contains a single variant of this Product")
        self.assertEquals(len(i_variants),
                          2,
                          "fixture has 2 variants of the Holy Napkin")
        icon_v1 = i_variants[0]
        self.assertIsInstance(icon_v1, ProductInventory)
