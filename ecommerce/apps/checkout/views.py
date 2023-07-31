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

from ecommerce.apps.accounts.forms import UserAddressForm
from ecommerce.apps.accounts.models import Address
from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.inventory.models import Stock
from ecommerce.apps.orders.models import Order, OrderItem

config = dotenv_values()

logger = logging.getLogger("django")

# TODO: switch to prod
square_client = Client(
    access_token=config["SQUARE_ACCESS_TOKEN"], environment="sandbox"
)


def deliverychoices(request):
    return render(request, "checkout/delivery_choices.html", {})


def payment_selection(request):
    session = request.session
    purchase = session.get("purchase")
    address = session.get("address")
    if not address:
        return redirect("catalogue:home")
    address_json = json.loads(session.get("address"))

    full_name = address_json.get("full_name")
    address_line1 = address_json.get("address_line1")
    address_line2 = address_json.get("address_line2")
    city_locality = address_json.get("city_locality")
    state_province = address_json.get("state_province")
    postal_code = address_json.get("postal_code")
    country_code = address_json.get("country_code")

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

    if request.user.is_authenticated:
        logger.debug(f"user is authenticated")
        addresses = Address.objects.filter(customer=request.user).order_by(
            "-default"
        )

        if len(addresses) == 0:
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
            logger.debug(f"address in session:\n {a}")
            address = json.loads(a)
            return render(
                request,
                "checkout/delivery_choices.html",
                {
                    "addresses": [address],
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


# https://developer.squareup.com/forums/t/django-csrf-middleware-token-missing/6959
@api_view(["POST"])
def payment_with_token(request):
    session = request.session
    _id, shipping_price, tier, _days = (
        session.get("purchase").get("delivery_choice").split("/")
    )

    token = request.data.get("payload").get("source_id")
    if not token:  # is it even possible though?
        logger.error("payment_with_token must have a token (source_id)")
        res = JsonResponse(
            {"success": False, "message": "Token missing"}, status=400
        )
        return res
    session = request.session
    total_s = session.get("purchase")["total"]
    total_i = int(float(total_s) * 100)

    refid = "".join(random.choices(string.ascii_lowercase, k=10))

    payload = {
        "source_id": token,
        "idempotency_key": "".join(
            random.choices(string.ascii_lowercase, k=18)
        ),
        "amount_money": {"amount": total_i, "currency": "USD"},
        "app_fee_money": {"amount": 0, "currency": "USD"},
        "autocomplete": True,
        "location_id": settings.SQUARE_LOCATION_ID,
        "reference_id": refid,
    }

    logger.info(f"create_payment payload: {payload}")

    result = square_client.payments.create_payment(body=payload)

    logger.info(f"Square API call resulted in:\n{result.body}")

    if result.is_success():
        basket = Basket(request)
        address_json = session["address"]
        address_d = json.loads(request.session["address"])

        try:
            fname, lname = json.loads(address_json).get("full_name").split(" ")
        except ValueError:
            fname = lname = ""
        user = request.user
        order = Order.objects.create(
            user=user if user.is_authenticated else None,
            full_name=f"{fname} {lname}",
            email=user.email
            if user.is_authenticated
            else "someone@example.com",
            address_line1=address_d.get("address_line1"),
            address_line2=address_d.get("address_line2"),
            city=address_d.get("city_locality"),
            postal_code=address_d.get("postal_code"),
            country_code=address_d.get("country_code"),
            total_paid=total_i / 100,
            payment_option="Square",
            paid=True,
            shipping_price=shipping_price,
            shipping_method=tier,
        )

        order.kind = "GENERIC"
        for sku, item in basket.basket.items():
            stock = Stock.objects.get(sku=sku)
            if "x" in sku:
                order.kind = "ENL_OR_RED"
                continue
            elif sku.startswith("L-"):
                order.kind = "INCENSE"
            
            OrderItem.objects.create(
                order_id=order.pk,
                title=item["title"],
                sku=stock,
                price=item["price"],
                quantity=item["qty"],
            )

        order.save()
        logger.info(f"new order created: {order}, clearing the basket")
        basket.clear()
        response = JsonResponse({"result": result.body, "success": True})

        return response
    else:
        logger.error(result.errors)
        return JsonResponse({"success": False, "message": result.text})
