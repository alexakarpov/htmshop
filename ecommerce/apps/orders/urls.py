from django.urls import path

from .views import (
    OrderDetails,
    PrintOrders,
    ListOrders,
    orders_of_kind,
    add_payment,
)

app_name = "orders"

urlpatterns = [
    path("", ListOrders.as_view(), name="list"),
    path("<int:pk>", OrderDetails.as_view(), name="details"),
    path("print/", PrintOrders.as_view(), name="print"),
    path("payment/", add_payment, name="add_payment"),
]
