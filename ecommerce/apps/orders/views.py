from typing import Any

from django.http import HttpRequest, HttpResponse
from django.views.generic import ListView

from .models import Order


class ListOrders(ListView):
    template_name = "orders_list.html"
    model = Order

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)


def user_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id)
    return orders
