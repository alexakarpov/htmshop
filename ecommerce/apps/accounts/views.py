import logging

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


from ecommerce.apps.catalogue.models import Product
from ecommerce.apps.orders.models import Order

from .forms import RegistrationForm, UserAddressForm, UserEditForm
from .models import Address
from .tokens import account_activation_token


logger = logging.getLogger("django")

UserModel = get_user_model()


@login_required
def wishlist(request):
    products = Product.objects.filter(users_wishlist=request.user)
    return render(
        request,
        "accounts/dashboard/user_wish_list.html",
        {"wishlist": products},
    )


@login_required
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    if product.users_wishlist.filter(id=request.user.id).exists():
        product.users_wishlist.remove(request.user)
        messages.success(
            request, product.title + " has been removed from your WishList"
        )
    else:
        product.users_wishlist.add(request.user)
        messages.success(
            request, "Added " + product.title + " to your WishList"
        )
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def dashboard(request):
    logger.debug(f"accounts - dashboard for {request.user}")

    return render(
        request,
        "accounts/dashboard/dashboard.html",
        {
            "section": "profile",
        },
    )


@login_required
def edit_details(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)

        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)

    return render(
        request,
        "accounts/dashboard/edit_details.html",
        {"user_form": user_form},
    )


@login_required
def delete_user(request):
    user = UserModel.objects.get(email=request.user)
    user.is_active = False
    user.save()
    logout(request)
    return redirect("accounts:delete_confirmation")


def register_account(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.email = registerForm.cleaned_data["email"]
            user.first_name = registerForm.cleaned_data["first_name"]
            user.last_name = registerForm.cleaned_data["last_name"]
            user.set_password(registerForm.cleaned_data["password"])
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = "Activate your Account"
            message = render_to_string(
                "accounts/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            user.email_user(subject=subject, message=message)
            logger.debug(f"Registration email sent to {user.email}")
            return render(
                request,
                "accounts/register_email_confirm.html",
                {"form": registerForm},
            )
        else:
            logger.debug("INVALID FORM")
            return render(
                request, "accounts/register.html", {"form": registerForm}
            )
    else:
        registerForm = RegistrationForm()
    return render(request, "accounts/register.html", {"form": registerForm})


def account_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        login(
            request,
            user,
            backend="ecommerce.apps.accounts.auth_backend.EmailAuthBackend",
        )
        return redirect("accounts:dashboard")
    else:
        return render(request, "accounts/activation_invalid.html")


######### Addresses ###########


#### Authenticated User ###########
@login_required
def view_address(request):
    addresses = Address.objects.filter(customer=request.user)
    return render(
        request, "accounts/dashboard/addresses.html", {"addresses": addresses}
    )


@login_required
def add_address(request):
    if request.method == "POST":
        address_form = UserAddressForm(data=request.POST)
        if address_form.is_valid():
            logger.debug("address is valid")
            address_form = address_form.save(commit=False)
            address_form.customer = request.user
            address_form.save()
            return HttpResponseRedirect(reverse("accounts:addresses"))
        else:
            logger.error("invalid address")
            for error in address_form.errors:
                logger.error(error)
            return HttpResponse("Error handler content", status=400)
    else:
        address_form = UserAddressForm()
    return render(
        request,
        "accounts/dashboard/edit_addresses.html",
        {"form": address_form},
    )


@login_required
def edit_address(request, id):
    if request.method == "POST":
        address = Address.objects.get(pk=id, customer=request.user)
        address_form = UserAddressForm(instance=address, data=request.POST)
        if address_form.is_valid():
            address_form.save()
            return HttpResponseRedirect(reverse("accounts:addresses"))
    else:
        address = Address.objects.get(pk=id.hex, customer=request.user)
        address_form = UserAddressForm(instance=address)
    return render(
        request,
        "accounts/dashboard/edit_addresses.html",
        {"form": address_form},
    )


@login_required
def delete_address(request, id):
    address = Address.objects.filter(pk=id, customer=request.user).delete()
    return redirect("accounts:addresses")


@login_required
def set_default(request, id):
    Address.objects.filter(pk=id).update(default=True)
    Address.objects.exclude(pk=id).update(default=False)
    previous_url = request.META.get("HTTP_REFERER")

    if "delivery_address" in previous_url:
        return redirect("checkout:delivery_address")

    return redirect("accounts:addresses")


@login_required
def user_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id)
    return render(
        request, "accounts/dashboard/user_orders.html", {"orders": orders}
    )
