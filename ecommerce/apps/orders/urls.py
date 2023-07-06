from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("list/", views.ListOrders.as_view(), name="list"),
]
