b = [
    {"price": "30.00", "qty": 1, "variant": "8x10",
     "title": "Holy Napkin", "weight": 16},
    {"price": "20.00", "qty": 1, "variant": "",
     "title": "Prayer Book", "weight": 8}
]

a = Address()
a.full_name = "John Doe"
a.address_line = "1 Main St"
a.postcode = "98765"
s = make_shipment(b, a)
