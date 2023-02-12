from django import forms

from .models import Stock, ProductInventory
from ecommerce.constants import ROOMS


class MoveStockForm(forms.Form):
    from_room = forms.ChoiceField(label="From", choices=ROOMS)
    to_room = forms.ChoiceField(label="To", choices=ROOMS)
    qty = forms.IntegerField(
        label="Quantity",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "quantity"}),
    )
    sku = forms.ModelChoiceField(
        queryset=ProductInventory.objects.filter(
            product_type__name="mounted icon"
        )
    )
