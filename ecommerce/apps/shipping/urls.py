from django.urls import path, re_path
from rest_framework import routers, serializers, viewsets


from . import views

app_name = "shipping"

urlpatterns = [
    path(
        "",
        views.shipstation,
        #   views.OrderExportView.as_view(),
        name="get_orders",
    ),
    path("get-rates/", views.get_rates, name="shipping_get_rates"),
]
