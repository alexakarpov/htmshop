import ast
import json
import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from ecommerce.apps.accounts.models import Address
from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.orders.models import Order, OrderItem
from ecommerce.apps.shipping.choice import ShippingChoice, split_tiers
from ecommerce.apps.shipping.engine import shipping_choices
from ecommerce.utils import debug_print

logger = logging.getLogger("django")


@login_required
def deliverychoices(request):
    return render(request, "checkout/delivery_choices.html", {})


@login_required
def payment_selection(request):
    session = request.session
    total = session["purchase"]["total"]
    if "address" not in request.session:
        messages.success(request, "Please select an address")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    return render(request, "checkout/payment_selection.html", {"total": total})


def basket_update_delivery(request):
    basket = Basket(request)
    if request.POST.get("action") == "post":
        opts = request.POST.get("deliveryoption")
        debug_print(opts)
        [_, sprice, _, _] = opts.split("/")
        total = basket.basket_get_total(sprice)
        total = str(total)
        session = request.session
        if "purchase" not in request.session:
            session["purchase"] = {"delivery_choice": opts, "total": total}
        else:
            session["purchase"]["delivery_choice"] = opts
            session["purchase"]["total"] = total
            session.modified = True

        response = JsonResponse({"total": total, "delivery_price": sprice})
        return response


@login_required
def delivery_address(request):
    basket = Basket(request)

    session = request.session
    session["purchase"] = {}

    addresses = Address.objects.filter(customer=request.user).order_by("-default")

    if "address" not in request.session:
        session["address"] = {"address_id": str(addresses[0].id)}
        session.modified = True
    else:
        session["address"]["address_id"] = str(addresses[0].id)
        session.modified = True
    return render(
        request,
        "checkout/delivery_address.html",
        {
            "addresses": addresses,
        },
    )


####
# PayPal
####
from paypalcheckoutsdk.orders import OrdersGetRequest

from .paypal import PayPalClient


@login_required
def payment_complete(request):
    PPClient = PayPalClient()
    logger.info("in payment_complete")
    body = json.loads(request.body)
    logger.info(f"{body}")  # there's just an orderId for now?
    data = body["orderID"]
    user_id = request.user.id

    requestorder = OrdersGetRequest(data)
    logger.info(f">>>>>>>>> {requestorder} <<<<<<<<")
    response = PPClient.client.execute(requestorder)

    total_paid = response.result.purchase_units[0].amount.value

    basket = Basket(request)
    order = Order.objects.create(
        user_id=user_id,
        full_name=response.result.purchase_units[0].shipping.name.full_name,
        email=response.result.payer.email_address,
        address1=response.result.purchase_units[0].shipping.address.address_line_1,
        address2=response.result.purchase_units[0].shipping.address.admin_area_2,
        postal_code=response.result.purchase_units[0].shipping.address.postal_code,
        country_code=response.result.purchase_units[0].shipping.address.country_code,
        total_paid=response.result.purchase_units[0].amount.value,
        order_key=response.result.id,
        payment_option="paypal",
        billing_status=True,
    )
    order_id = order.pk

    for item in basket:
        OrderItem.objects.create(order_id=order_id, product=item["product"], price=item["price"], quantity=item["qty"])

    print("Order created?!")

    return JsonResponse("Payment completed!", safe=False)


@login_required
def payment_successful(request):
    basket = Basket(request)
    basket.clear()  # address is missing from the session?!
    return render(request, "checkout/payment_successful.html", {})
