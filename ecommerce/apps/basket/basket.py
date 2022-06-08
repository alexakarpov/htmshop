import json
import logging
from decimal import Decimal

from django.conf import settings
from ecommerce.apps.catalogue.models import Product

logger = logging.getLogger("django")


class Basket:
    """
    A base Basket class, providing some default behaviors that
    can be inherited or overrided, as necessary.
    """

    def __init__(self, request):
        self.session = request.session
        basket = self.session.get(settings.BASKET_SESSION_KEY)
        if settings.BASKET_SESSION_KEY not in request.session:
            basket = self.session[settings.BASKET_SESSION_KEY] = {}
        self.basket = basket

    def add(self, product, qty, variant=None):
        """
        Adding and updating the users basket session data
        """
        print(f"adding {product.id}({product.title}) to cart in {self.session.session_key}")
        product_id = str(product.id)
        if product_id in self.basket:
            self.basket[product_id]["qty"] = qty
            self.basket[product_id]["title"] = product.title
            self.basket[product_id]["weight"] = product.weight
            if variant:
                self.basket[product_id]["variant"] = variant
        else:
            self.basket[product_id] = {
                "price": str(product.price),
                "qty": qty,
                "variant": variant,
                "title": product.title,
                "weight": product.weight,
            }

        self.save()

    def __iter__(self):
        """
        Collect the product_id in the session data to query the database
        and return products
        Need to rewrite this, so that the template has access to the variants,
        which are not DB-based, but only live in the session.
        """
        product_ids = self.basket.keys()
        products = Product.objects.filter(id__in=product_ids)
        basket = self.basket.copy()

        for product in products:
            basket[str(product.id)]["product"] = product

        for item in basket.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["qty"]
            yield item

    def __len__(self):
        """
        Get the basket data and count the qty of items
        """
        print("in Basket's len")
        return sum(item["qty"] for item in self.basket.values())

    def update(self, product_id, qty):
        """
        Update values in session data
        """
        print(f"updating {product_id} in cart {self.session.session_key}")

        product_id = str(product_id)
        if product_id in self.basket:
            self.basket[product_id]["qty"] = qty
        self.save()

    def get_subtotal_price(self):
        return sum(Decimal(item["price"]) * item["qty"] for item in self.basket.values())

    def basket_get_total(self, deliveryprice=0):
        subtotal = sum(Decimal(item["price"]) * item["qty"] for item in self.basket.values())
        total = subtotal + Decimal(deliveryprice)
        return total

    def delete(self, product_id):
        """
        Delete item from session data
        """
        print(f"deleting {product_id} from cart in {self.session.session_key}")

        product_id = str(product_id)

        if product_id in self.basket:
            del self.basket[product_id]
            self.save()

    def clear(self):
        # Remove basket from session
        del self.session[settings.BASKET_SESSION_KEY]
        del self.session["address"]
        del self.session["purchase"]
        self.save()

    def save(self):
        self.session.modified = True

    def toJSON(self):
        return json.dumps(self.basket, indent=2)

    def __str__(self):
        return self.basket.__str__()


def get_weight(basket_ds):
    print(f"basket_ds: {basket_ds}")
    total = 0
    for it in basket_ds:
        w = it["weight"]
        q = it["qty"]
        total += w * q

    return total
