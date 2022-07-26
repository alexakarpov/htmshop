#!/usr/bin/env python

from django.conf import settings
from dotenv import dotenv_values
from square.client import Client

config = dotenv_values()


client = Client(
    access_token=config['SQUARE_ACCESS_TOKEN'],
    environment='sandbox')

body = {}
body['source_id'] = "cnon:CBASEJjdQjlYeviAuQVr6dbcfqQ"
body['idempotency_key'] = '7b0f3ec5-086a-4871-8f13-3c81b3875218'
body['amount_money'] = {}
body['amount_money']['amount'] = 1000
body['amount_money']['currency'] = 'USD'
body['app_fee_money'] = {}
body['app_fee_money']['amount'] = 10
body['app_fee_money']['currency'] = 'USD'
body['autocomplete'] = True
body['customer_id'] = 'W92WH6P11H4Z77CTET0RNTGFW8'
body['location_id'] = settings.SQUARE_LOCATION_ID
body['reference_id'] = '123456'
body['note'] = 'Brief description'

result = client.payments.create_payment(body)


if result.is_success():
    print(result.body)
    for location in result.body['locations']:
        print(f"{location['id']}: ", end="")
        print(f"{location['name']}, ", end="")
        print(f"{location['address']['address_line_1']}, ", end="")
        print(f"{location['address']['locality']}")

elif result.is_error():
    for error in result.errors:
        print(error['category'])
        print(error['code'])
        print(error['detail'])
