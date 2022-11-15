# from .forms import StaxPaymentForm
# from square.client import Client
# import hashlib
import json
import logging
from uuid import uuid4

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
from ecommerce.apps.catalogue.models import ProductInventory
from ecommerce.apps.orders.models import Order, OrderItem

# from .paypal import PayPalClient

# from paypalcheckoutsdk.orders import OrdersGetRequest


config = dotenv_values()

POST_URL = "https://secure.networkmerchants.com/api/transact.php"
SALE = "sale"

logger = logging.getLogger("console")


# @login_required
def deliverychoices(request):
    logger.debug(">> checkout deliverychoices")
    return render(request, "checkout/delivery_choices.html", {})


# @login_required
def payment_selection(request):
    session = request.session
    total = session["purchase"]["total"]
    return render(request, "checkout/payment_selection.html", {"total": total})


def basket_update_delivery(request):
    basket = Basket(request)
    if request.POST.get("action") == "post":
        opts = request.POST.get("deliveryoption")
        logger.debug(f"delivery option selected: {opts}")
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


def delivery_address(request):
    logger.debug(f">> checkout delivery_address with {request.method}")
    session = request.session
    session["purchase"] = {}

    # everetgyng is simple if they are logged in:
    if request.user.is_authenticated:
        logger.debug(f"user is authenticated")
        addresses = Address.objects.filter(customer=request.user).order_by(
            "-default"
        )

        if len(addresses) == 0:
            # messages.warning(
            #     request, "Enter an address for the checkout")
            logger.debug(f"no addresses yet")

            return HttpResponseRedirect(reverse("accounts:addresses"))

        if "address" not in request.session:
            logger.debug("no address in session for authenticated user")
            session["address"] = addresses[0].toJSON()
            session.modified = True
        else:
            address_json = session["address"]
            logger.debug(f"Address in session:\n {address_json}")
            address_dict = json.loads(address_json)
            address_obj = Address.from_dict(address_dict)
            logger.debug(f"address object: {address_obj}")
            addresses = [address_obj]

        return render(
            request,
            "checkout/delivery_address.html",
            {
                "addresses": addresses,
            },
        )
    # guest user
    else:
        if "address" not in request.session:
            logger.debug("no address in session for guest user")
            messages.warning(request, "Enter an address for the checkout")

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
    logger.debug(f"| checkout guest_address with {request.method}")

    if request.method == "POST":
        session = request.session
        address_form = UserAddressForm(data=request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            session["address"] = address.toJSON()
            logger.debug(
                "| form processed, address saved in the session, redirectong to delivery_address"
            )
            return HttpResponseRedirect(reverse("checkout:delivery_address"))
        else:
            logger.error("invalid address")
            for error in address_form.errors:
                logger.error(error)
            return HttpResponse("Error handler content", status=400)
    else:
        address_form = UserAddressForm()
        return render(
            request, "checkout/guest_address.html", {"form": address_form}
        )


def report(logger, res_text):
    logger.debug("REPORTING")

    for i in res_text.split("&"):
        (k, v) = i.split("=")
        logger.debug(f"{k} => {v}")


def payment_with_token(request):
    payment_token = request.POST["payment_token"]
    logger.debug(f"processing payment with token: {payment_token}")
    session = request.session
    basket = Basket(request)

    # for k in session.keys():
    #     logger.debug(f"session key {k}, value {session.get(k)}")

    # for k, v in config.items():
    #     logger.debug(f"{k} is {v}")

    address_json = session["address"]
    total = session["purchase"]["total"]

    # AnonymousUser doesn't have these
    if request.user.is_authenticated:
        user = request.user
        fname = user.get_first_name()
        lname = user.get_last_name()
    else:
        # can't we do this for a logged in user?
        try:
            fname, lname = json.loads(address_json).get("full_name").split(" ")
        except ValueError:
            fname = lname = ""

    ############### while working on Orders, skip the payment POST

    # response = requests.post(
    #     POST_URL,
    #     params={
    #         "security_key": config["STAX_SECURITY_KEY"],
    #         "amount": total,
    #         "type": SALE,
    #         "payment_token": payment_token,
    #         "first_name": fname,
    #         "last_name": lname,
    #     },
    #     headers={},
    # )

    # if not response:
    #     logger.error("RESPONSE ERROR")

    ############# end of skip

    # report(logger, response.text)

    # ok. a successful payment means the order was placed, so need to capture it in a model
    # order data requires address and cart (already in the session)

    user = request.user
    address_json = request.session["address"]
    address_d = json.loads(address_json)

    if user.is_authenticated:
        logger.debug(f"{user} is authenticated")
        user = user
    else:
        logger.debug(f"{user} is NOT authenticated")

    logger.debug(f"placing an order for {user} ({type(user)})")  # FIXME
    # fails for an anonyumous user

    order = Order.objects.create(
        user=user,
        full_name=f"{fname} {lname}",
        email=user.email
        if user.is_authenticated
        else "someone@example.com",  # FIXME
        address1=address_d.get("address_line1"),
        address2=address_d.get("address_line2"),
        postal_code=address_d.get("postal_code"),
        country_code=address_d.get("country_code"),
        total_paid=total,
        order_key=str(uuid4()),
        payment_option="Stax",
        billing_status=True,
    )
    order_id = order.pk

    for sku, item in basket.basket.items():
        pii = ProductInventory.objects.get(sku=sku)
        OrderItem.objects.create(
            order_id=order_id,
            inventory_item=pii,
            price=item["price"],
            quantity=item["qty"],
        )

    order.save()

    basket.clear()

    messages.info(
        request,
        f"Your order has been placed, reference key: {order.order_key}",
    )

    return HttpResponseRedirect(reverse("catalogue:store_home"))


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
