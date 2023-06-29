from typing import Any

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.views.generic import ListView

from ecommerce.constants import LINES_PER_PAGE

from .models import Order


class ListOrders(ListView):
    template_name = "orders_list.html"
    model = Order

    def get_context_data(self, **kwargs):
        orders = Order.objects.all()  # TODO: narrow this
        paginator = Paginator(orders, 1)

        return {"pages": paginator}


def user_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id)
    return orders
