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

logger = logging.getLogger("django")


@login_required
def deliverychoices(request):
    deliveryoptions = [
        {"delivery_name": "aaa", "delivery_timeframe": "2 days", "delivery_price": "31.00"},
        {"delivery_name": "bbb", "delivery_timeframe": "5 days", "delivery_price": "11.00"},
    ]
    return render(request, "checkout/delivery_choices.html", {"deliveryoptions": deliveryoptions})


@login_required
def payment_selection(request):
    session = request.session
    if "address" not in request.session:
        messages.success(request, "Please select address option")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    return render(request, "checkout/payment_selection.html", {})


def basket_update_delivery(request):
    # print("==== in basket_update_delivery =====")
    basket = Basket(request)
    if request.POST.get("action") == "post":
        # convert string repr of a dict to dict
        od = ast.literal_eval(request.POST.get("deliveryoption"))
        updated_total_price = basket.basket_update_delivery(od.get("delivery_price"))
        session = request.session
        if "purchase" not in request.session:
            session["purchase"] = {
                "delivery_choice": od,
            }
        else:
            session["purchase"]["delivery_choice"] = od
            session.modified = True

        response = JsonResponse({"total": updated_total_price, "delivery_price": od.get("delivery_price")})
        return response


@login_required
def delivery_address(request):
    print("in delivery_address")
    basket = Basket(request)

    session = request.session
    delivery_choice = session["purchase"]["delivery_choice"]
    print(f"DELCHOICE:>>{delivery_choice}")
    if "purchase" not in request.session:
        messages.success(request, "Please select delivery option")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    addresses = Address.objects.filter(customer=request.user).order_by("-default")

    if "address" not in request.session:
        session["address"] = {"address_id": str(addresses[0].id)}
    else:
        session["address"]["address_id"] = str(addresses[0].id)
        session.modified = True
    subtotal = Decimal(basket.get_subtotal_price())
    delivery_price = Decimal(delivery_choice.get("delivery_price"))
    total = delivery_price + subtotal
    return render(
        request,
        "checkout/delivery_address.html",
        {"addresses": addresses, "delivery_price": delivery_price, "total_price": total},
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
