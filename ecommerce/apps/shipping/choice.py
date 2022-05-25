class ShippingChoice:
    name = ""
    price = 0
    days = 1
    id = ""

    def __init__(self, rate_d) -> None:
        self.name = rate_d.get("service_code")
        self.price = rate_d.get("shipping_amount").get("amount")
        self.id = rate_d.get("rate_id")
        self.days = rate_d.get("delivery_days")

    def __repr__(self):
        return f"{self.id}:{self.price} / {self.name} / {self.days}"


def rate_to_choice(rate):
    return ShippingChoice(rate)
