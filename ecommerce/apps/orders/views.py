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

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        print(f"got inside with {kwargs}")
        context = super().get_context_data(**kwargs)
        return context


class ListOrders(ListView):
    model = Order
    template_name = "orders/manage.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return context


def user_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id)
    return orders

def orders_of_kind(request, kind):
    orders = Order.objects.filter(kind=kind)
    return render(request, "orders/order_list.html", {"orders": list(orders)})
