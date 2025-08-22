# import json
import logging, decimal
from typing import Any

# from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.http import JsonResponse
from rest_framework.decorators import api_view
from datetime import date
from django.db.models import F

# from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.shipping.choice import ShippingChoiceSE, split_tiers
from ecommerce.apps.shipping.engine import (
    shipping_choices_for_order,
)

from ecommerce.apps.catalogue.models import Product
from ecommerce.apps.inventory.models import Stock
from ecommerce.apps.shipping.serializers import ShippingChoiceSESerializer
from ecommerce.constants import DAYS_LATE

from .models import Order, OrderItem, Payment, Collection

logger = logging.getLogger(__name__)


class PrintOrders(ListView):
    template_name = "print_orders.html"
    model = Order

    def get_context_data(self, **kwargs):
        orders = Order.objects.filter(status__iexact="PROCESSING")
        # print(f"{orders.count()} orders to print")
        return {"orders": orders}


class OrderDetails(DetailView):
    model = Order

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx_data = super().get_context_data(**kwargs)
        outstanding = self.object.order_total - self.object.total_paid
        ctx_data["outstanding"] = outstanding
        products = Product.objects.filter(is_active=True).order_by("title")
        ctx_data["products"] = products

        return ctx_data


class Invoice(DetailView):
    model = Order
    template_name = "orders/order_print.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx_data = super().get_context_data(**kwargs)
        outstanding = self.object.order_total - self.object.total_paid
        ctx_data["outstanding"] = outstanding
        return ctx_data


class ListOrders(ListView):
    model = Order
    template_name = "orders/order_list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kind = self.request.GET.get("kind")
        ctx = super().get_context_data(**kwargs)
        if kind and kind.lower() != "all":
            orders = Order.objects.filter(kind__icontains=kind)
            ctx = {"order_list": orders, "kind": kind}
        return ctx


#@api_view(["GET"])
class Collections(ListView):
    model = Collection
    template_name = "orders/collection_calls.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        collects = Collection.objects.all()
        ctx = super().get_context_data(**kwargs)
        ctx["collections"] = collects
        return ctx


class LateOnPaymentOrders(ListView):
    model = Order
    template_name = "orders/payment_late.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        orders_in_processing = Order.objects.filter(
            status="PROCESSING"
        ).filter(total_paid__lt=F("order_total"))

        late = []

        for o in orders_in_processing:
            diff = (date.today() - o.created_at).days
            if diff > DAYS_LATE:
                late.append(o)

        ctx = super().get_context_data(**kwargs)
        ctx["order_list"] = late
        return ctx


def add_payment(request):
    amount = decimal.Decimal((request.POST.get("amount")))
    comment = request.POST.get("comment")
    oid = request.POST.get("oid")
    order = Order.objects.get(id=oid)
    p = Payment.objects.create(amount=amount, comment=comment, order=order)
    order.total_paid += amount
    if order.total_paid >= order.order_total:
        order.status = "PROCESSING"
    order.save()
    return JsonResponse(
        {"message": f"{p.pk} created", "amount": amount}, status=200
    )


def user_orders(request):
    user_id = request.user.id
    return Order.objects.filter(user_id=user_id)


@api_view(["POST"])
def fix_product(request):
    product_slug = request.POST.get("slug")
    p = Product.objects.get(slug=product_slug)
    stocks = p.get_skus()

    skus = [stock.sku for stock in stocks.all()]

    return JsonResponse({"skus": skus})


@api_view(["POST"])
def append(request):
    sku = request.POST.get("sku")
    order_id = int(request.POST.get("order"))
    qty = int(request.POST.get("qty"))
    stock = Stock.objects.get(sku=sku)
    order = Order.objects.get(id=order_id)
    new_item = OrderItem()
    new_item.product = stock.product
    new_item.order = order
    new_item.stock = stock
    new_item.quantity = qty
    new_item.save()
    order.items.add(new_item)
    order.subtotal += stock.price * qty
    order.save()
    return JsonResponse({"success": True})


@api_view(["POST"])
def recalculate(request):
    order_id = request.POST.get("order_id")
    order = Order.objects.get(id=order_id)
    intl = order.country_code != "US"
    try:
        choices: list[ShippingChoiceSE] = shipping_choices_for_order(
            order
        )  # now need to split tiers and extract 3
    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})

    if not order.is_first_class():
        choices = [
            x for x in choices if x.service_code != "usps_first_class_mail"
        ]

    # 13.28/se-6550365789/usps_ground_advantage/5 <- a choice
    tiers = split_tiers(choices, international=intl)

    express_choice: ShippingChoiceSE = sorted(tiers["express"])[0]
    regular_choice: ShippingChoiceSE = sorted(tiers["regular"])[0]
    fast_choice: ShippingChoiceSE = sorted(tiers["fast"])[0]

    serializer = ShippingChoiceSESerializer(
        [regular_choice, fast_choice, express_choice], many=True
    )

    sub = order.calculate_subtotal()
    return JsonResponse({"sub_price": sub, "tiers": serializer.data})
