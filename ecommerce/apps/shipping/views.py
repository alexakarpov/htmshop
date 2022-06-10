import json

from django.http import JsonResponse
from ecommerce.apps.accounts.models import Address
from ecommerce.apps.basket.basket import Basket
from ecommerce.apps.shipping.choice import ShippingChoice

# from ecommerce.apps.shipping.choice import ShippingChoice, ShippingChoiceEncoder
from ecommerce.apps.shipping.engine import shipping_choices
from ecommerce.utils import debug_print
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import ShippingChoiceSerializer


@api_view(http_method_names=["GET"])
def get_rates(request):
  basket = Basket(request)
  session = request.session
  address_id = session["address"]["address_id"]
  address = Address.objects.get(id=address_id)
  choices = shipping_choices(basket, address)
  serializer = ShippingChoiceSerializer(choices, many=True)
  sdata=serializer.data
  return JsonResponse({"choices": sdata})
