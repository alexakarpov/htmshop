from django.urls import path

from .views import (
    OrderDetails,
    Invoice,
    PrintOrders,
    ListOrders,
    LateOnPaymentOrders,
    add_payment,
    fix_product,
    append,
    recalculate
)

app_name = "orders"

urlpatterns = [
    path("", ListOrders.as_view(), name="list"),
    path("<int:pk>", OrderDetails.as_view(), name="details"),
    path("print/", PrintOrders.as_view(), name="print"),
    path("late/", LateOnPaymentOrders.as_view(), name="payment_late"),
    path("payment/", add_payment, name="add_payment"),
    path("invoice/<int:pk>", Invoice.as_view(), name="invoice"),
    path("fix_product/", fix_product, name="fix_product"),
    path("append/", append, name="append"),
    path("recalculate/", recalculate, name="recalculate"),
]
