from django.views.generic import ListView

from ecommerce.constants import LINES_PER_PAGE

from .models import Order


class PrintOrders(ListView):
    template_name = "print_orders.html"
    model = Order

    def get_context_data(self, **kwargs):
        orders = Order.objects.filter(status__iexact="PENDING")
        return {"orders": orders}

class ManageOrders(ListView):
    # template_name = "orders.html"
    # model = Order

    # def get_context_data(self, **kwargs):
    #     orders = Order.objects.filter(status__iexact="PENDING")
    #     return {"orders": orders}
    pass

def user_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id)
    return orders
