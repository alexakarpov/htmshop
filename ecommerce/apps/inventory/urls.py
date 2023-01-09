from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.inventory_index, name="inventory_dash"),
]
