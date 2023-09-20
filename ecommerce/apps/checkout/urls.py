from django.urls import include, path

from . import views

app_name = "checkout"

urlpatterns = [
    path("deliverychoices", views.deliverychoices, name="deliverychoices"),
    path(
        "basket_update_delivery/",
        views.basket_update_delivery,
        name="basket_update_delivery",
    ),
    path("delivery_address/", views.delivery_address, name="delivery_address"),
    path("payment_selection/", views.payment_selection, name="payment_selection"),
    #     path("payment_complete/", views.payment_complete, name="payment_complete"),
    path("payment/", views.payment_with_token, name="token_payment"),
    path("pay_later/", views.pay_later, name="pay_later"),
    path("guest_address/", views.guest_address, name="guest_address"),
]
