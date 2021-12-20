from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from store.models import Category, Product

class TestBasketView(TestCase):
    def setUp(self):
        User.objects.create(username='admin')
        Category.objects.create(name='django', slug='django')
        Product.objects.create(category_id=1, title='django beginners', created_by_id=1,
                               slug='django-beginners', price='10.00', image='django')
        Product.objects.create(category_id=1, title='django intermediate', created_by_id=1,
                               slug='django-beginners', price='20.00', image='django')
        Product.objects.create(category_id=1, title='django advanced', created_by_id=1,
                               slug='django-beginners', price='30.00', image='django')

    def test_basket_url(self):
        """
        Test homepage response status
        """
        response = self.client.get(reverse('basket:basket_summary'))
        self.assertEqual(response.status_code, 200)

    def test_basket_add(self):
        """
        Test adding items to the basket
        """
        response = self.client.post(
            reverse('basket:basket_add'), {"productid": 3, "productqty": 1, "action": "post"}, xhr=True)
        self.assertEqual(response.json(), {'qty': 1})

        response = self.client.post(
            reverse('basket:basket_add'), {"productid": 2, "productqty": 1, "action": "post"}, xhr=True)
        # 1 of #3 and 1 of #2
        self.assertEqual(response.json(), {'qty': 2})

        response = self.client.post(
            reverse('basket:basket_add'), {"productid": 2, "productqty": 3, "action": "post"}, xhr=True)
        # change qty of #2 to 3
        self.assertEqual(response.json(), {'qty': 4})

    def test_basket_delete(self):
        """
        Test deleting items from the basket
        """

        # reuse the adding actions from previous test
        self.client.post(reverse('basket:basket_add'), {"productid": 3, "productqty": 1, "action": "post"}, xhr=True)
        self.client.post(reverse('basket:basket_add'), {"productid": 2, "productqty": 1, "action": "post"}, xhr=True)

        # ..and now perform the deletion
        response = self.client.post(
            reverse('basket:basket_delete'), {"productid": 2, "action": "post"}, xhr=True)
        self.assertEqual(response.json(), {'qty': 1, 'subtotal': '30.00'})

    def test_basket_update(self):
        """
        Test updating items from the basket
        """
        # reuse the adding actions from previous test
        self.client.post(reverse('basket:basket_add'),
         {"productid": 3,
          "productqty": 3,
           "action": "post"},
           xhr=True)
        self.client.post(
            reverse('basket:basket_add'), {"productid": 2, "productqty": 2, "action": "post"}, xhr=True)

        # and now update
        response = self.client.post(
            reverse('basket:basket_update'), {"productid": 2, "productqty": 1, "action": "post"}, xhr=True)
        self.assertEqual(response.json(), {'qty': 4, 'subtotal': '110.00'})
