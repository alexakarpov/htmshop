from django.views.generic import ListView

from ecommerce.constants import LINES_PER_PAGE

from .models import Order


class ListOrders(ListView):
    template_name = "orders.html"
    model = Order

    def get_context_data(self, **kwargs):
        orders = Order.objects.all()  # TODO: narrow this
        return {"orders": orders}


def user_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id)
    return orders
