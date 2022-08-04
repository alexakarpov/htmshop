#! /usr/bin/env python

from types import CoroutineType
import requests

print(requests.__version__)
POST_URL = 'https://secure.networkmerchants.com/api/transact.php'

SALE = 'sale'
SECURITY_KEY = ''
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
