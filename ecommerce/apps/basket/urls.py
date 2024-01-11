from django.urls import path

from . import views

app_name = "basket"

urlpatterns = [
    path("", views.basket_summary, name="summary"),
    path("add/", views.basket_add, name="add"),
    path("delete/", views.basket_delete, name="delete"),
    path("update/", views.basket_update, name="update"),
]
