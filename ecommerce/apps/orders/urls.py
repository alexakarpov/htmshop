from django.urls import path

from .views import (
    OrderDetails,
    Invoice,
    PrintOrders,
    ListOrders,
    LateOnPaymentOrders,
    orders_of_kind,
    add_payment,
    amend,
    append,
    discount
)

app_name = "orders"

urlpatterns = [
    path("", ListOrders.as_view(), name="list"),
    path("<int:pk>", OrderDetails.as_view(), name="details"),
    path("print/", PrintOrders.as_view(), name="print"),
    path("late/", LateOnPaymentOrders.as_view(), name="payment_late"),
    path("amend/", amend, name="amend"),
    path("append/", append, name="append"),
    path("bookstore-discount", discount, name="bookstore-discount"),
    path("payment/", add_payment, name="add_payment"),
    path("invoice/<int:pk>", Invoice.as_view(), name="invoice")
]
