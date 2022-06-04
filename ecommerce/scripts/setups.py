import json

from ecommerce.apps.shipping.choice import ShippingChoice, rate_to_choice

with open("shipping_jsons/get_rates_response.json") as f:
    j=json.load(f)
    rates=j.get('rate_response').get('rates')
    choices = list(map(lambda r: rate_to_choice(r), rates))
    print("loaded rates:", len(rates))

print("inits completed")
