import logging, decimal
from typing import Any, Dict
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.http import HttpResponseRedirect, JsonResponse
from rest_framework.decorators import api_view
from datetime import date, timedelta

from ecommerce.apps.catalogue.models import Product
from ecommerce.apps.inventory.models import Stock
from ecommerce.constants import DAYS_LATE

from .models import Order, OrderItem, Payment

logger = logging.getLogger("django")


class PrintOrders(ListView):
    template_name = "print_orders.html"
    model = Order

    def get_context_data(self, **kwargs):
        orders = Order.objects.filter(status__iexact="PROCESSING")
        print(f"{orders.count()} orders to print")
        return {"orders": orders}


class OrderDetails(DetailView):
    model = Order

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx_data = super().get_context_data(**kwargs)
        outstanding = self.object.order_total - self.object.total_paid
        ctx_data["outstanding"] = (
            outstanding
        )

        products = Product.objects.filter(is_active=True).order_by("title")
        ctx_data["products"] = products
        # print(f"{products.count()} products to select")
        # print(ctx_data)
        return ctx_data


@api_view(["POST"])
def amend(request):
    product_slug = request.POST.get("slug")
    order_id = int(request.POST.get("order"))
    order = Order.objects.get(id=order_id)
    p = Product.objects.get(slug=product_slug)
    stocks = p.get_skus()
    skus = [stock.sku for stock in stocks.all()]

    return JsonResponse({"skus": skus})


@api_view(["POST"])
def append(request):
    # print(f"append POST came in: { request.POST}")
    sku = request.POST.get("sku")
    order_id = int(request.POST.get("order"))
    qty = int(request.POST.get("qty"))
    stock = Stock.objects.get(sku=sku)

    order = Order.objects.get(id=order_id)
    new_item = OrderItem()
    new_item.order = order
    new_item.quantity = qty
    new_item.stock = stock
    new_item.price = stock.price
    new_item.title = stock.product.title
    new_item.save()
    order.save()
    return JsonResponse({"success": True})


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


class LateOnPaymentOrders(ListView):
    model = Order
    template_name = "orders/payment_late.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        all = Order.objects.filter(status="PROCESSING")
        month = timedelta(days=30)
        td = date.today()

        late = []

        for o in all:
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
    orders = Order.objects.filter(user_id=user_id)
    return orders


def orders_of_kind(request, kind):
    orders = Order.objects.filter(kind=kind)
    return render(request, "orders/order_list.html", {"orders": orders})
