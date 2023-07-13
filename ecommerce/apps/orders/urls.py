from django.urls import path

from .views import OrderDetails, PrintOrders, ManageOrders

app_name = "orders"

urlpatterns = [
    path("<int:pk>", OrderDetails.as_view(), name="order_details"),
    path("print/", PrintOrders.as_view(), name="print"),
    path("manage/", ManageOrders.as_view(), name="manage")
]
