from django.urls import path

from .views import OrderDetails, PrintOrders, ListOrders, orders_of_kind

app_name = "orders"

urlpatterns = [
    path("<int:pk>", OrderDetails.as_view(), name="order_details"),
    path("print/", PrintOrders.as_view(), name="print"),
    path("manage/", ListOrders.as_view(), name="manage"),
    path("<str:kind>", orders_of_kind, name="ofkind"),
]
