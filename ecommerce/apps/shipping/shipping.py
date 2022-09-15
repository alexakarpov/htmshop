import json

from shipengine import ShipEngine
from shipengine.errors import ShipEngineError

SE_SANDBOX_KEY = "TEST_pTjqOjvNiKsTgNXKGtLi1jWEzUuDadyhO4uLfQSzXWw"
shipengine = ShipEngine(
    {"api_key": SE_SANDBOX_KEY, "page_size": 75, "retries": 3, "timeout": 10}
)


USPS_ID = "se-660215"
FEDEX_ID = "se-660217"
UPS_ID = "se-660216"

test_shipment = {
    "rate_options": {
        "carrier_ids": [USPS_ID, UPS_ID, FEDEX_ID],
        "service_codes": [
            # "usps_priority_mail_express",
            # "usps_parcel_select",
            # "usps_media_mail"
        ],
        "package_types": ["package"],
    },
    "shipment": {
        "validate_address": "no_validation",
        "ship_to": {
            "name": "Amanda Miller",
            "phone": "555-555-5555",
            "address_line1": "525 S Winchester Blvd",
            "city_locality": "San Jose",
            "state_province": "CA",
            "postal_code": "95128",
            "country_code": "US",
            "address_residential_indicator": "yes",
        },
        "ship_from": {
            "name": "Shipping department",
            "company_name": "Holy Transfiguration Monastery",
            "phone": "617-734-0608",
            "address_line1": "278 Warren St",
            "city_locality": "Brookline",
            "state_province": "MA",
            "postal_code": "02445",
            "country_code": "US",
            "address_residential_indicator": "yes",
        },
        "packages": [{"weight": {"value": 2, "unit": "pound"}}],
    },
}


def list_carriers(engine=shipengine):
    return engine.list_carriers()


def dumpit(json_data, fname):
    with open(fname, "w") as json_file:
        json_file.truncate(0)
        json.dump(json_data, json_file, indent=4)
        json_file.write("\n")  # Add newline 'cause Py JSON does not


def get_rates(engine=shipengine, shipment=test_shipment):
    return engine.get_rates_from_shipment(shipment=test_shipment)


if __name__ == "__main__":
    try:
        rates = get_rates(shipengine, test_shipment)
        print(json.dumps(rates, indent=4))
    except ShipEngineError as err:
        print("::ERROR::")
        print(err.to_json())
