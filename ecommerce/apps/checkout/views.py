from distutils.log import debug
from .paypal import PayPalClient
from ecommerce.utils import debug_print
from ecommerce.apps.orders.models import Order, OrderItem
from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.accounts.models import Address
from django.contrib import messages
from paypalcheckoutsdk.orders import OrdersGetRequest
from dotenv import dotenv_values
from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import EmptyForm
# from square.client import Client
import hashlib
import json
import logging
import requests

config = dotenv_values()

POST_URL = 'https://secure.networkmerchants.com/api/transact.php'
SALE = 'sale'

logger = logging.getLogger("django")


@login_required
def deliverychoices(request):
    return render(request, "checkout/delivery_choices.html", {})


@login_required
def payment_selection(request):
    session = request.session
    total = session["purchase"]["total"]
    token = session["purchase"]["token"]
    form = EmptyForm()
    return render(request, "checkout/payment_selection.html", {"total": total,
                                                               "idempotency_token": token,
                                                               "form": form})


def basket_update_delivery(request):
    basket = Basket(request)
    if request.POST.get("action") == "post":
        opts = request.POST.get("deliveryoption")
        debug_print(opts)
        [_, sprice, _, _] = opts.split("/")
        total = basket.get_total(sprice)
        total = str(total)
        token = hashlib.md5(str(basket).encode())
        debug_print(token)
        session = request.session
        if "purchase" not in request.session:
            session["purchase"] = {"delivery_choice": opts, "total": total}
        else:
            session["purchase"]["delivery_choice"] = opts
            session["purchase"]["total"] = total

        session["purchase"]["token"] = token.hexdigest()
        session.modified = True
        response = JsonResponse({"total": total, "delivery_price": sprice})
        return response


@login_required
def delivery_address(request):
    session = request.session
    session["purchase"] = {}

    addresses = Address.objects.filter(
        customer=request.user).order_by("-default")

    if len(addresses) == 0:
        messages.warning(
            request, "Enter an address for the checkout")

        return HttpResponseRedirect(reverse("accounts:addresses"))

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


def payment_with_token(request):
    payment_token = request.POST['payment_token']
    session = request.session
    total = session["purchase"]["total"]

    # debug_print(request.POST)
    response = requests.post(
        POST_URL,
        params={'security_key': config["STAX_SECURITY_KEY"],
                'amount': total,
                'type': SALE,
                'payment_token': payment_token
                },
        headers={},
    )
    return HttpResponseRedirect(reverse('catalogue:store_home'))
    # return HttpResponseRedirect(reverse('checkout:payment_successful'))
    # source_id = request.POST.get('source')
    # config = dotenv_values()
    # sq_access_token = config["SQUARE_ACCESS_TOKEN"]
    # sq_env = settings.SQUARE_ENVIRONMENT
    # client = Client(access_token=sq_access_token, environment=sq_env)

    # body = {}
    # body['source_id'] = source_id
    # body['idempotency_key'] = '7b0f3ec5-086a-4871-8f13-3c81b3875218'
    # body['amount_money'] = {}
    # body['amount_money']['amount'] = 888
    # body['amount_money']['currency'] = 'USD'

    # result = client.payments.create_payment(body)

    # if result.is_success():
    #     debug_print("SUCCESS")
    #     return(JsonResponse({"message": "ok"}))
    # elif result.is_error():
    #     debug_print("ERROR")
    #     return(JsonResponse({"message": "notok"}))


####
# PayPal
####


@ login_required
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
        OrderItem.objects.create(
            order_id=order_id, product=item["product"], price=item["price"], quantity=item["qty"])

    print("Order created?!")

    return JsonResponse("Payment completed!", safe=False)


@login_required
def payment_successful(request):
    basket = Basket(request)
    basket.clear()  # address is missing from the session?!
    return render(request, "checkout/payment_successful.html", {})
