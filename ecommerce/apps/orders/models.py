from decimal import Decimal

from django.conf import settings
from django.db import models

from ecommerce.apps.catalogue.models import ProductInventory


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_user",
        null=True,
    )
    full_name = models.CharField(max_length=150, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    address1 = models.CharField(max_length=250, null=False, blank=False)
    address2 = models.CharField(max_length=250)
    city = models.CharField(max_length=100, null=False, blank=False)
    phone = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country_code = models.CharField(max_length=4, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total_paid = models.DecimalField(max_digits=5, decimal_places=2)
    order_key = models.CharField(max_length=200)
    payment_option = models.CharField(max_length=200, blank=True)
    billing_status = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"order# {self.id} by {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.CASCADE
    )
    inventory_item = models.ForeignKey(
        ProductInventory, related_name="order_items", on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=5, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"order {self.order.id} item"
        


def make_order(address_d, cart_d, email):
    o = Order()
    o.full_name = address_d["full_name"]
    
    total = 0
    for sku, item in cart_d.items():
        total += float(item.get("price")) * int(item.get("qty"))

    o.total_paid = total
    o.email = email
    return o

    # def get_total(self, deliveryprice=0):
    #     subtotal = sum(Decimal(item["price"]) * item["qty"]
    #                    for item in self.basket.values())
    #     total = subtotal + Decimal(deliveryprice)
    #     return total
