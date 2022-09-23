# from .forms import StaxPaymentForm
# from square.client import Client
# import hashlib
import json
import logging

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from dotenv import dotenv_values

from ecommerce.apps.accounts.forms import UserAddressForm
from ecommerce.apps.accounts.models import Address
from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.orders.models import Order, OrderItem
from ecommerce.utils import debug_print

# from .paypal import PayPalClient

# from paypalcheckoutsdk.orders import OrdersGetRequest


config = dotenv_values()

POST_URL = 'https://secure.networkmerchants.com/api/transact.php'
SALE = 'sale'

logger = logging.getLogger("console")


# @login_required
def deliverychoices(request):
    logger.debug(">> checkout deliverychoices")
    return render(request, "checkout/delivery_choices.html", {})


# @login_required
def payment_selection(request):
    user = request.user
    debug_print(f"user:\n{user}")

    session = request.session
    total = session["purchase"]["total"]
    # form = StaxPaymentForm(
    # initial = {'cc_firstname': user.get_first_name(), 'cc_lastname': user.get_last_name()})
    return render(request, "checkout/payment_selection.html", {"total": total,
                                                               #    "idempotency_token": token,
                                                               #    "form": form
                                                               })


def basket_update_delivery(request):
    basket = Basket(request)
    if request.POST.get("action") == "post":
        opts = request.POST.get("deliveryoption")
        debug_print(f"delivery option selected: {opts}")
        [_, sprice, _, _] = opts.split("/")
        total = basket.get_total(sprice)
        total = str(total)
        # token = hashlib.md5(str(basket).encode())
        session = request.session
        if "purchase" not in request.session:
            session["purchase"] = {"delivery_choice": opts, "total": total}
        else:
            session["purchase"]["delivery_choice"] = opts
            session["purchase"]["total"] = total

        session.modified = True
        response = JsonResponse({"total": total, "delivery_price": sprice})
        return response


# @ login_required
def delivery_address(request):
    logger.debug(">> checkout delivery_address")
    session = request.session
    session["purchase"] = {}

    # everetgyng is simple if they are logged in:
    if request.user.is_authenticated:
        addresses = Address.objects.filter(
            customer=request.user).order_by("-default")

        if len(addresses) == 0:
            # messages.warning(
            #     request, "Enter an address for the checkout")

            return HttpResponseRedirect(reverse("accounts:addresses"))

        if "address" not in request.session:
            logger.debug("no address in session for authenticated user")
            session["address"] = addresses[0].toJSON()
            session.modified = True
        else:
            address_json = session["address"]
            logger.debug(f"Address in session:\n {address_json}")
            address_dict = json.loads(address_json)
            addresses = [Address(address_dict)]

        return render(
            request,
            "checkout/delivery_address.html",
            {
                "addresses": addresses,
            },
        )
    #guest user
    else:
        if "address" not in request.session:
            logger.debug("no address in session for guest user")
            messages.warning(
                request, "Enter an address for the checkout")

            return HttpResponseRedirect(reverse("checkout:guest_address"))

        else:
            a = session.get("address")
            logger.debug(f"Address in session:\n {a}")
            address = json.loads(a)
            return render(
                request,
                "checkout/delivery_choices.html",
                {
                    "addresse   s": [address],
                },
            )

def guest_address(request):
    logger.debug(">> checkput guest_address")

    if request.method == "POST":
        session = request.session
        address_form = UserAddressForm(data=request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            logger.debug(type(address))

            session["address"] = address.toJSON()
            logger.debug(">> REDIRECTING")
            return HttpResponseRedirect(reverse("checkout:delivery_address"))
        else:
            logger.error("invalid address")
            for error in address_form.errors:
                logger.error(error)
            return HttpResponse("Error handler content", status=400)
    else:
        address_form = UserAddressForm()
    return render(request, "checkout/guest_address.html", {"form": address_form})


def report(logger, res_text):
    logger.debug("REPORTING")

    for i in res_text.split('&'):
        (k, v) = i.split('=')
        logger.debug(f"{k} => {v}")


def payment_with_token(request):
    payment_token = request.POST['payment_token']
    debug_print(
        f"processing payment with token: {payment_token}")
    session = request.session

    d = {}

    for k in session.keys():
        d[k] = session.get(k)

    debug_print(f"session keys:\n {d}")

    user = request.user
    fname = user.get_first_name()
    lname = user.get_last_name()

    total = session["purchase"]["total"]

    # debug_print(request.POST)
    response = requests.post(
        POST_URL,
        params={'security_key': config["STAX_SECURITY_KEY"],
                'amount': total,
                'type': SALE,
                'payment_token': payment_token,
                'first_name': fname,
                'last_name': lname
                },
        headers={},
    )

    if response:
        print("RESPONSE *OK*")
    else:
        print("RESPONSE *ERROR*")

    report(response.text)

    return HttpResponseRedirect(reverse('catalogue:store_home'))

####
# PayPal
####


# @ login_required
# def payment_complete(request):
#     PPClient = PayPalClient()
#     logger.info("in payment_complete")
#     body = json.loads(request.body)
#     logger.info(f"{body}")  # there's just an orderId for now?
#     data = body["orderID"]
#     user_id = request.user.id

#     requestorder = OrdersGetRequest(data)
#     logger.info(f">>>>>>>>> {requestorder} <<<<<<<<")
#     response = PPClient.client.execute(requestorder)

#     total_paid = response.result.purchase_units[0].amount.value

#     basket = Basket(request)
#     order = Order.objects.create(
#         user_id=user_id,
#         full_name=response.result.purchase_units[0].shipping.name.full_name,
#         email=response.result.payer.email_address,
#         address1=response.result.purchase_units[0].shipping.address.address_line_1,
#         address2=response.result.purchase_units[0].shipping.address.admin_area_2,
#         postal_code=response.result.purchase_units[0].shipping.address.postal_code,
#         country_code=response.result.purchase_units[0].shipping.address.country_code,
#         total_paid=response.result.purchase_units[0].amount.value,
#         order_key=response.result.id,
#         payment_option="paypal",
#         billing_status=True,
#     )
#     order_id = order.pk

#     for item in basket:
#         OrderItem.objects.create(
#             order_id=order_id, product=item["product"], price=item["price"], quantity=item["qty"])

#     print("Order created?!")

#     return JsonResponse("Payment completed!", safe=False)


# @ login_required
def payment_successful(request):
    basket = Basket(request)
    basket.clear()
    return render(request, "checkout/payment_successful.html", {})
