import json
import logging
import random
import string

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from dotenv import dotenv_values
from rest_framework.decorators import api_view
from square.client import Client

from ecommerce.apps.accounts.forms import UserAddressForm, GuestAddressForm
from ecommerce.apps.accounts.models import Address
from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.inventory.models import Stock
from ecommerce.apps.orders.models import Order, OrderItem, Payment

config = dotenv_values()

logger = logging.getLogger(__name__)

# TODO: switch to prod
square_client = Client(
    access_token=config["SQUARE_ACCESS_TOKEN"], environment="sandbox"
)


def classify_order_add_items(order: Order, basket: Basket):
    """
    - classifies order between generic, enlargement/reduction and incense
    - creates OrderItems and attaches them to order
    """
    order.kind = "GENERIC"  # default
    for sku, item in basket.basket.items():
        stock = Stock.objects.get(sku=sku)
        if "x" in sku:
            order.kind = "ENL_OR_RED"
        elif sku.startswith("L-"):
            order.kind = "INCENSE" if order.kind == "GENERIC" else "ENL_OR_RED"
        qty = item["qty"]

        stock.wrapping_remove(qty)
        stock.save()
        OrderItem.objects.create(
            order_id=order.pk,
            stock=stock,
            quantity=qty,
        )
    order.save()
    return


def deliverychoices(request):
    return render(request, "checkout/delivery_choices.html", {})


def payment_selection(request):
    session = request.session
    purchase = session.get("purchase")
    address = session.get("address")

    if not address:
        logger.error("Address isn't in session")
        return redirect("catalogue:home")  # is this a right redirect?!
    address_json = json.loads(session.get("address"))
    full_name = address_json.get("full_name")
    address_line1 = address_json.get("address_line1")
    address_line2 = address_json.get("address_line2")
    city_locality = address_json.get("city_locality")
    state_province = address_json.get("state_province")
    postal_code = address_json.get("postal_code")
    # guest users have 'country' in there
    country_code = address_json.get("country_code") or address_json.get(
        "country"
    )

    total = purchase["total"] if purchase else 0
    app_id = settings.SQUARE_APP_ID
    location_id = settings.SQUARE_LOCATION_ID
    return render(
        request,
        "checkout/payment_selection.html",
        {
            "app_id": app_id,
            "location_id": location_id,
            "total": total,
            "trusted": request.user.is_authenticated
            and request.user.is_trusted and request.user.creditable(total),
            "full_name": full_name,
            "address_line1": address_line1,
            "address_line2": address_line2,
            "city_locality": city_locality,
            "state_province": state_province,
            "postal_code": postal_code,
            "country_code": country_code,
        },
    )


def basket_update_delivery(request):
    basket = Basket(request)
    if request.POST.get("action") == "post":
        opts = request.POST.get("deliveryoption")
        logger.warning(f"delivery option selected: {opts}")
        tier_name, shipping_price, service_code = opts.split("/")
        total = str(basket.get_total(delivery_cost=shipping_price))

        # token = hashlib.md5(str(basket).encode())
        session = request.session
        if "purchase" not in request.session:
            session["purchase"] = {"delivery_choice": opts, "total": total}
        else:
            session["purchase"]["delivery_choice"] = opts
            session["purchase"]["total"] = total

        session.modified = True
        return JsonResponse(
            {
                "total": total,
                "delivery_price": shipping_price,
                "service_code": service_code,
            }
        )


def delivery_address(request):
    session = request.session
    session["purchase"] = {}

    if request.user.is_authenticated:
        addresses = Address.objects.filter(customer=request.user).order_by(
            "-default"
        )

        if addresses.count() == 0:
            return HttpResponseRedirect(reverse("accounts:addresses"))

        if "address" not in request.session:
            session["address"] = addresses[0].toJSON()
            session.modified = True

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
            messages.warning(request, "Enter an address for the checkout")

            return HttpResponseRedirect(reverse("checkout:guest_address"))

        else:
            a = session.get("address")
            address = json.loads(a)
            return render(
                request,
                "checkout/delivery_choices.html",
                {
                    "addresses": [address],
                },
            )


def guest_address(request):
    if request.method == "POST":
        session = request.session
        address_form = GuestAddressForm(data=request.POST)
        if address_form.is_valid():
            # address = address_form.save(commit=False)
            session["address"] = json.dumps(request.POST)
            return HttpResponseRedirect(reverse("checkout:delivery_address"))
        else:
            logger.error("invalid address")
            for error in address_form.errors:
                logger.error(error)
            return HttpResponse("Error handler content", status=400)
    else:
        address_form = GuestAddressForm()
        return render(
            request, "checkout/guest_address.html", {"form": address_form}
        )


@api_view(["POST"])
def pay_later(request):
    session = request.session
    choice = session.get("purchase").get("delivery_choice")
    tier_name, shipping_cost, service_code = choice.split("/")
    basket = Basket(request)
    address_json = session["address"]
    address_d = json.loads(address_json)
    full_name = address_d.get("full_name")

    user = request.user

    order = Order.objects.create(
        user=user if user.is_authenticated else None,
        phone=address_d.get("phone"),
        full_name=full_name,
        email=user.email if user.is_authenticated else address_d.get("email"),
        address_line1=address_d.get("address_line1"),
        address_line2=address_d.get("address_line2"),
        city_locality=address_d.get("city_locality"),
        postal_code=address_d.get("postal_code"),
        state_province=address_d.get("state_province"),
        country_code=address_d.get("country_code"),
        subtotal=basket.get_subtotal_price(),
        total_paid=0,
        payment_option="Later",
        status="PROCESSING",
        shipping_cost=shipping_cost,
        shipping_method=tier_name.upper(),
    )

    classify_order_add_items(order, basket)
    basket.clear()

    return JsonResponse({}, status=200)


# https://developer.squareup.com/forums/t/django-csrf-middleware-token-missing/6959
@api_view(["POST"])
def payment_with_token(request):
    basket = Basket(request)
    session = request.session
    choice = session.get("purchase").get("delivery_choice")
    tier_name, shipping_cost, service_code = choice.split("/")

    token = request.data.get("payload").get("source_id")
    if not token:  # is it even possible though?
        logger.error("payment_with_token must have a token (source_id)")
        return JsonResponse(
            {"success": False, "message": "Token missing"}, status=400
        )
    session_total_str = session.get("purchase")["total"]
    total_i = int(float(session_total_str) * 100)

    reference_id = "".join(random.choices(string.ascii_lowercase, k=10))

    payload = {
        "source_id": token,
        "idempotency_key": "".join(
            random.choices(string.ascii_lowercase, k=18)
        ),
        "amount_money": {"amount": total_i, "currency": "USD"},
        "app_fee_money": {"amount": 0, "currency": "USD"},
        "autocomplete": True,
        "location_id": settings.SQUARE_LOCATION_ID,
        "reference_id": reference_id,
    }

    result = square_client.payments.create_payment(body=payload)

    if result.is_success():
        basket = Basket(request)
        address_json = session["address"]
        address_d = json.loads(address_json)

        full_name = json.loads(address_json).get("full_name")

        user = request.user

        order = Order.objects.create(
            user=user if user.is_authenticated else None,
            full_name=full_name,
            email=(
                user.email if user.is_authenticated else address_d.get("email")
            ),
            address_line1=address_d.get("address_line1"),
            address_line2=address_d.get("address_line2"),
            city_locality=address_d.get("city_locality"),
            postal_code=address_d.get("postal_code"),
            country_code=address_d.get("country_code"),
            total_paid=float(session_total_str),
            phone=address_d.get("phone"),
            payment_option="Square",
            state_province=address_d.get("state_province"),
            status="PROCESSING",
            shipping_cost=shipping_cost,
            shipping_method=tier_name.upper(),
            subtotal=basket.get_subtotal_price(),  # Decimal(session_total_str),
        )

        classify_order_add_items(order, basket)
        basket.clear()
        return JsonResponse({"result": result.body, "success": True})
    else:
        logger.error(result.errors)
        return JsonResponse({"success": False, "message": result.text})
