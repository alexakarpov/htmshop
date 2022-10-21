from django.test import TestCase

from ecommerce.apps.catalogue.models import Product, ProductType, ProductSpecification


class ProductTest(TestCase):
    fixtures = ['catalogue.json', ]

    def test_fixture_worked(self):
        self.assertEquals(Product.objects.all().count(),
                          2, "fixture has 2 Productss")

    def test_product_types_and_specs(self):
        p1 = Product.objects.get(slug="pb")
        p2 = Product.objects.get(slug="hn")
        self.assertEqual(p1.title, "Prayer book", "fixture works, expected product loaded")

        book = p1.product_type
        icon = p2.product_type
        p1_specs =  p1.product_type.productspecification_set.all()
        p2_specs =  p2.product_type.productspecification_set.all()
        all_specs = ProductSpecification.objects.all()
        book_specs = all_specs.filter(product_type=book)
        icon_specs = all_specs.filter(product_type=icon)
        self.assertEquals(book_specs.count(), 2, "there should be two specs for books")
        self.assertEquals(icon_specs.count(), 3, "there should be three specs for icons")
        spec = book_specs.first() # cmon, this isn't testing
        self.assertIn(spec, p1_specs, "Book's spec is in books specs")

    def test_type_name(self):
        book = ProductType.objects.get(pk=1)
        self.assertEquals(book.name, "book")

    def test_product_get_variants(self):
        book_p = Product.objects.get(slug="pb")
        icon_p = Product.objects.get(slug="hn")
        b_variants = book_p.get_variants()
        i_variants = icon_p.get_variants()
        self.assertEquals(len(b_variants), 1, "fixture contains a single variant of this Product")
        self.assertEquals(len(i_variants), 2, "fixture has 2 variants of the Holy Napkin")
