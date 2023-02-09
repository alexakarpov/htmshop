from django import forms

from .models import Stock, ProductInventory
from ecommerce import constants


ROOMS = [(1, "Sanding room"), (2, "Mounting room"), (3, "Printing room")]


class MoveStockForm(forms.Form):
    from_room = forms.ChoiceField(label="From", choices=ROOMS)
    to_room = forms.ChoiceField(label="To", choices=ROOMS)
    qty = forms.IntegerField(label="Quantity", min_value=0)
    sku = forms.ModelChoiceField(
        queryset=ProductInventory.objects.filter(
            product_type__name="mounted icon"
        )
    )
