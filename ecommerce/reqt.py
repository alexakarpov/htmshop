#! /usr/bin/env python

import requests
from dotenv import dotenv_values

config = dotenv_values()

POST_URL = 'https://secure.networkmerchants.com/api/transact.php'
QUERY_URL = 'https://secure.networkmerchants.com/api/query.php'

SALE = 'sale'

SECURITY_KEY = config["STAX_SECURITY_KEY"]
amount = '11'
descriptor = "something"
tax = '-1'
# shipping = ''  # total shipping amount?
# ponumber = ''  # orignal order #
# first_name = ''
# last_name = ''

# address_1
# address_2
# city
# state
# zip
# country# phone
# email


# response = 3
# &responsetext = Authentication Failed
# &authcode =
# &transactionid = 0
# &avsresponse =
# &cvvresponse =
# &orderid =
# &type =
# &response_code = 300

def report(res_text):

    for i in res_text.split('&'):
        (k, v) = i.split('=')
        print(f"{k} => {v}")


if __name__ == "__main__":
    response = requests.post(
        POST_URL,
        params={'security_key': SECURITY_KEY,
                'amount': '12.99',
                'type': SALE,
                'payment_token': '00000000-000000-000000-000000000000'
                },
        headers={},
    )

    if response:
        print("SUCCESS")
        print(response.headers)
        print("----------------------------------")
        report(response.text)
    else:
        print("ERROR")
        report(response.text)
