from django import forms
from .models import Room, ProductInventory
from .utils import filter_inventory
from ecommerce import constants


class MoveStockForm(forms.Form):
    rooms = Room.objects.all()
    inv = filter_inventory(
        ProductInventory.objects.all(), constants.MOUNTED_ICON_TYPE_NAME
    )
    room_choices = []
    sku_choices = []
    for r in rooms:
        c = (r.pk, r.name)
        room_choices.append(c)
    skus = []
    for i in inv:
        s = (i.sku, i.sku)
        sku_choices.append(s)

    from_room = forms.ChoiceField(label="From", choices=room_choices)

    to_room = forms.ChoiceField(label="To", choices=room_choices)
    sku = forms.ChoiceField(label="Product Inventory SKU", choices=sku_choices)
    qty = forms.IntegerField(label="Quantity", min_value=0)
