#!/usr/bin/env python

from square.client import Client

from dotenv import dotenv_values

config = dotenv_values()


client = Client(
    access_token=config['SQUARE_ACCESS_TOKEN'],
    environment='sandbox')


result = client.locations.list_locations()

if result.is_success():
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
