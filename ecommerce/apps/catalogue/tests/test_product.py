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
        self.assertEqual(p1.title, "Prayer book")

        book = p1.product_type
        icon = p2.product_type
        p1_specs =  p1.product_type.productspecification_set.all()
        p2_specs =  p2.product_type.productspecification_set.all()
        self.assertEquals(p1_specs.count(), 2, "there are 2 specs for a book")
        self.assertEquals(p2_specs.count(), 3, "there are 3 specs for an icon")
        all_specs = ProductSpecification.objects.all()
        book_specs = all_specs.filter(product_type=book)
        icon_specs = all_specs.filter(product_type=icon)
        self.assertEquals(book_specs.count(), 2, "there should be two specs for books")
        self.assertEquals(icon_specs.count(), 3, "there should be two specs for books")
        spec = book_specs.first()
        self.assertIn(spec, book_specs, "Book's spec is in books specs")

    def test_type_name(self):
        book = ProductType.objects.get(pk=1)
        self.assertEquals(book.name, "book")
