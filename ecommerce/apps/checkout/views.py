from .forms import EmptyForm
import hashlib
import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from dotenv import dotenv_values
from paypalcheckoutsdk.orders import OrdersGetRequest
from square.client import Client

from ecommerce.apps.accounts.models import Address
from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.orders.models import Order, OrderItem
from ecommerce.utils import debug_print

from .paypal import PayPalClient

logger = logging.getLogger("django")


@login_required
def deliverychoices(request):
    return render(request, "checkout/delivery_choices.html", {})


@login_required
def payment_selection(request):
    session = request.session
    total = session["purchase"]["total"]
    token = session["purchase"]["token"]
    return render(request, "checkout/payment_selection.html", {"total": total,
                                                               "idempotency_token": token})


def basket_update_delivery(request):
    basket = Basket(request)
    if request.POST.get("action") == "post":
        opts = request.POST.get("deliveryoption")
        debug_print(opts)
        [_, sprice, _, _] = opts.split("/")
        total = basket.basket_get_total(sprice)
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


def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        debug_print(request.POST)

        # create a form instance and populate it with data from the request:
        form = EmptyForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            print("done processing, redirecting to '/'")
            return HttpResponseRedirect('/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EmptyForm()

    return render(request, 'checkout/name.html', {'form': form})


def payment_with_token(request):
    debug_print(request.POST)
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

    return(JsonResponse({"message": "ok"}))

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


@ login_required
def payment_successful(request):
    basket = Basket(request)
    basket.clear()  # address is missing from the session?!
    return render(request, "checkout/payment_successful.html", {})
