from basket.basket import Basket
from django.shortcuts import render

import stripe
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from django.conf import settings
import logging

logger = logging.getLogger('django')


def order_placed(request):
    return render(request, 'payment/orderplaced.html')


class Error(TemplateView):
    template_name = 'payment/error.html'


@login_required
def BasketView(request):

    basket = Basket(request)
    total = basket.get_total_price()
    total_cents = int(total*100)
    print(total_cents)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    intent = stripe.PaymentIntent.create(
        amount=total_cents,
        currency='usd',
        metadata={'userid': request.user.id}
    )
    logger.debug(f"==========intent============\n{intent}")

    return render(request, 'payment/payment_form.html', {'client_secret': intent.client_secret,
                                                         'STRIPE_PUB_KEY': settings.STRIPE_PUBLISHABLE_KEY})
