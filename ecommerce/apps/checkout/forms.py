from django import forms
from django.forms.widgets import TextInput

from django.utils.translation import gettext_lazy as _


class StaxPaymentForm(forms.Form):
    cc_number = forms.CharField(
        label="CC number",
        required=True,
        max_length=19,
        error_messages={"required": "You will need a CC number"},
    )

    cc_firstname = forms.CharField(
        label="First name",
        required=True,
        max_length=5,
        help_text="Required",
        error_messages={
            "required": "Sorry, you will need a CC first name"},
    )

    cc_lastname = forms.CharField(
        label="Last name",
        required=True,
        max_length=3,
        help_text="Required",
        error_messages={"required": "Sorry, you will need a CC last name"},
    )
