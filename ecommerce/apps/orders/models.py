import functools
from typing import Any
from django.conf import settings
from django.db import models
from datetime import date

from ecommerce.apps.inventory.models import Stock
from ecommerce.constants import ORDER_STATUS, ORDER_KINDS


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_user",
        null=True,
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    address_line1 = models.CharField(max_length=250)
    address_line2 = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20)
    state_province = models.CharField(max_length=10)
    country_code = models.CharField(max_length=4, blank=True, default="US")
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    order_total = models.DecimalField(max_digits=7, decimal_places=2)
    total_paid = models.DecimalField(max_digits=7, decimal_places=2)
    payment_option = models.CharField(max_length=200, blank=True)
    paid = models.BooleanField(default=False)
    shipped = models.BooleanField(default=False)
    shipping_method = models.CharField(max_length=20)
    shipping_cost = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(
        choices=ORDER_STATUS, default="PENDING", max_length=10
    )
    kind = models.CharField(
        choices=ORDER_KINDS, default="GENERIC", max_length=10
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"order# {self.id} by {self.full_name} ({self.status})"

    def subtotal(self):
        return functools.reduce(
            lambda s, i: i.quantity * i.price + s, self.items.all(), 0
        )


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=100)
    sku = models.ForeignKey(Stock, on_delete=models.CASCADE, editable=False)

    price = models.DecimalField(max_digits=7, decimal_places=2, editable=False)

    def __str__(self):
        return f"{self.title} x {self.quantity}"


class Payment(models.Model):
    order = models.ForeignKey(
        Order, related_name="payments", on_delete=models.CASCADE
    )
    paid_at = models.DateField(auto_now=True)
    comment = models.CharField(blank=True, null=True, max_length=150)
    amount = models.DecimalField(decimal_places=2, max_digits=7)

    def __str__(self) -> str:
        return f"${self.amount} paid on {self.paid_at} ({self.comment})"
