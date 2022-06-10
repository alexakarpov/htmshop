from django.urls import path
from rest_framework import routers, serializers, viewsets

from . import views

app_name = "shipping"

urlpatterns = [
  path("get-rates/", views.get_rates, name="shipping_get_rates"),
]
