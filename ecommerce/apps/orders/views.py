from typing import Any, Dict
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from .models import Order


class PrintOrders(ListView):
    template_name = "print_orders.html"
    model = Order

    def get_context_data(self, **kwargs):
        orders = Order.objects.filter(status__iexact="PENDING")
        return {"orders": orders}


class OrderDetails(DetailView):
    model = Order


class ListOrders(ListView):
    model = Order
    template_name = "orders/manage.html"


def user_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id)
    return orders


def orders_of_kind(request, kind):
    orders = Order.objects.filter(kind=kind)
    return render(request, "orders/order_list.html", {"orders": orders})
