import logging, decimal
from typing import Any, Dict
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.http import HttpResponseRedirect, JsonResponse

from .models import Order, Payment

logger = logging.getLogger("django")


class PrintOrders(ListView):
    template_name = "print_orders.html"
    model = Order

    def get_context_data(self, **kwargs):
        orders = Order.objects.filter(status__iexact="PENDING")
        return {"orders": orders}


class OrderDetails(DetailView):
    model = Order

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx_data = super().get_context_data(**kwargs)
        ctx_data["outstanding"] = (
            self.object.order_total - self.object.total_paid
        )
        print(ctx_data)
        return ctx_data


class Invoice(DetailView):
    model = Order
    template_name = "orders/order_print.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx_data = super().get_context_data(**kwargs)
        ctx_data["outstanding"] = (
            self.object.order_total - self.object.total_paid
        )

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
        ctx = super().get_context_data(**kwargs)
        return ctx


def add_payment(request):
    amount = decimal.Decimal((request.POST.get("amount")))
    comment = request.POST.get("comment")
    oid = request.POST.get("oid")
    order = Order.objects.get(id=oid)
    p = Payment.objects.create(amount=amount, comment=comment, order=order)
    order.total_paid += amount
    if order.total_paid >= order.order_total:
        order.paid = True
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
