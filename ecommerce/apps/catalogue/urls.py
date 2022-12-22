from django.urls import path

from . import views

app_name = "catalogue"

urlpatterns = [
    path("", views.catalogue_index, name="store_home"),
    path("wip/", views.catalogue_new, name="new_home"),
    path("product/<slug:slug>", views.product_detail, name="product_detail"),
    path("<slug:category_slug>/", views.category_list, name="category_list"),
]
