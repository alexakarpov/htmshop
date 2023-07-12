from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("print/", views.PrintOrders.as_view(), name="print"),
    path("manage/", views.ManageOrders.as_view(), name="manage")
]
