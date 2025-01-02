from django.conf import settings
from django.db import models
import json

# from datetime import date, datetime
from decimal import Decimal
from django.db.models.signals import pre_save
from django.dispatch import receiver

from ecommerce.apps.inventory.models import Stock
from ecommerce.apps.catalogue.models import Product
from ecommerce.constants import ORDER_STATUS, ORDER_KINDS, SS_DT_FORMAT


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_user",
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    address_line1 = models.CharField(max_length=250)
    address_line2 = models.CharField(max_length=250, null=True, blank=True)
    city_locality = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, null=False, blank=False)
    postal_code = models.CharField(max_length=20)
    state_province = models.CharField(max_length=10)
    country_code = models.CharField(max_length=4, blank=True, default="US")
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    # order subtotal is the price of every item multiplied by it's quantity
    # ,same as Basket's subtotal
    subtotal = models.DecimalField(
        max_digits=7, decimal_places=2, null=False, blank=False
    )
    order_total = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )
    total_paid = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    payment_option = models.CharField(max_length=200, blank=True)
    shipping_method = models.CharField(
        choices=[
            ("REGULAR", "Regular"),
            ("FAST", "Fast"),
            ("EXPRESS", "Express"),
        ],
        blank=False,
        null=False,
        max_length=20,
    )
    shipping_cost = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(
        choices=ORDER_STATUS, default="PENDING", max_length=10
    )
    kind = models.CharField(
        choices=ORDER_KINDS, default="GENERIC", max_length=10
    )
    is_phone_order = models.BooleanField(default=False)
    is_bookstore_order = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"order# {self.id} by {self.full_name} ({self.created_at})"

    def paid(self):
        return self.total_paid >= self.order_total

    def shipped(self):
        return self.status == "SHIPPED"

    def format_created_at(self):
        return self.created_at.strftime(SS_DT_FORMAT)

    def format_updated_at(self):
        return self.updated_at.strftime(SS_DT_FORMAT)

    def to_dict(self):
        return {
            "full_name": self.full_name,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "phone": self.phone,
            "city_locality": self.city_locality,
            "state_province": self.state_province,
            "postal_code": self.postal_code,
            "country_code": self.country_code,
            "created_at": str(self.created_at),
        }

    def toJSON(self):
        return json.dumps(self.to_dict(), indent=2)

    def calculate_subtotal(self):
        sub = sum(i.item_total() for i in self.items.all())
        self.subtotal = sub
        self.save()
        return sub


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.CASCADE
    )

    #    product = models.ForeignKey(
    #        Product,
    #        related_name="products",
    #        on_delete=models.RESTRICT,
    #        null=True,
    #        blank=True,
    #       )

    stock = models.ForeignKey(
        Stock, related_name="stock", on_delete=models.CASCADE, null=True
    )

    quantity = models.PositiveIntegerField(default=1)

    def item_total(self):
        return self.stock.price * self.quantity

    def __str__(self):
        return (
            f"{self.stock.product.title} x {self.quantity}"
            if self.stock
            else "X"
        )

    def __repr__(self):
        return (
            f"{self.stock.product.title} x {self.quantity}"
            if self.stock
            else "X"
        )


class Payment(models.Model):
    order = models.ForeignKey(
        Order, related_name="payments", on_delete=models.CASCADE
    )
    paid_at = models.DateField(auto_now=True)
    comment = models.CharField(blank=True, null=True, max_length=150)
    amount = models.DecimalField(decimal_places=2, max_digits=7)

    def __str__(self) -> str:
        return f"${self.amount} paid on {self.paid_at} ({self.comment})"


@receiver(pre_save, sender=Order)
def set_order_total(sender, instance, **kwargs):
    instance.order_total = Decimal(instance.subtotal) + Decimal(
        instance.shipping_cost
    )
    return
