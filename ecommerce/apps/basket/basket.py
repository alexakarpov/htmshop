import logging
from decimal import Decimal

import simplejson as json
from django.conf import settings

from ecommerce.apps.inventory.models import Stock
from ecommerce.constants import PACKING_WEIGHT_MULTIPLIER

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

    def add(self, stock: Stock, qty: int, sku: str, price: Decimal):
        """
        Adding and updating the users basket session data
        product: actually a Stock
        qty: quantity of the item added
        pid: ProductInventory item's SKU, which acts as key in Basket's dict
        """

        # print(f"PRODUCT: {stock}, qty:{qty}, sku:{sku}, price: {price}")
        if sku in self.basket:
            self.basket[sku]["qty"] = qty
            self.basket[sku]["weight"] = json.dumps(stock.weight)
        else:
            self.basket[sku] = {
                "title": stock.product.title,
                "price": price,
                "qty": qty,
                "spec": stock.spec or "",
                "weight": json.dumps(stock.weight),
            }

        self.save()

    def __iter__(self):
        """
        Collect the product_id in the session data to query the database
        and return products
        Need to rewrite this, so that the template has access to the variants,
        which are not DB-based, but only live in the session.
        """
        skus = self.basket.keys()
        skus = Stock.objects.filter(sku__in=skus)
        basket = self.basket.copy()

        for s in skus:
            basket[str(s.sku)]["product"] = s

        for item in basket.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["qty"]
            yield item

    def __len__(self):
        """
        Get the basket data and count the qty of items
        """
        return sum(item["qty"] for item in self.basket.values())

    def update(self, sku, qty):
        """
        Update values in session data
        """
        if sku in self.basket:
            self.basket[sku]["qty"] = qty
        self.save()

    def get_subtotal_price(self):
        return sum(
            item["price"] * item["qty"] for item in self.basket.values()
        )

    def get_total(self, delivery_cost=0):
        subtotal = sum(
            item["price"] * item["qty"] for item in self.basket.values()
        )
        return round((subtotal + float(delivery_cost)), 2)

    def delete(self, sku):
        """
        Delete item from session data
        """
        logger.debug(f"deleting {sku} from cart in {self.session.session_key}")

        if sku in self.basket:
            del self.basket[sku]
            self.save()
        else:
            logger.debug("not found")

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
    total = 0
    for it in basket_ds:
        w = Decimal(it["weight"])
        q = it["qty"]
        total += w * q

    return float(total) * PACKING_WEIGHT_MULTIPLIER
