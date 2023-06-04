from django import forms
from django.utils.translation import gettext_lazy as _


class BillingAddressForm(forms.Form):
    full_name = forms.CharField(label="Full name", max_length=75)
    address_line1 = forms.CharField(label="Address line 1", max_length=150)
    address_line2 = forms.CharField(label="Address line 2", max_length=75)
    phone = forms.CharField(label="Phone", max_length=75)
    town_city = forms.CharField(label="Town/city", max_length=75)
    state_province = forms.CharField(label="State/province", max_length=75)
    postal_code = forms.CharField(label="Postal code", max_length=10)
    country = forms.CharField(label="Country", max_length=35)

    class Meta:
        fields = [
            "full_name",
            "phone",
            "address_line1",
            "address_line2",
            "town_city",
            "state_province",
            "postal_code",
            "country",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].widget.attrs.update(
            {"class": "form-control mb-2", "placeholder": _("full name")}
        )
        self.fields["phone"].widget.attrs.update(
            {"class": "form-control mb-2", "placeholder": _("phone")}
        )
        self.fields["address_line1"].widget.attrs.update(
            {"class": "form-control mb-2", "placeholder": _("address line 1")}
        )
        self.fields["address_line2"].widget.attrs.update(
            {"class": "form-control mb-2", "placeholder": _("address line 2")}
        )
        self.fields["town_city"].widget.attrs.update(
            {"class": "form-control mb-2", "placeholder": _("town/city")}
        )
        self.fields["state_province"].widget.attrs.update(
            {"class": "form-control mb-2", "placeholder": _("state/rovince")}
        )
        self.fields["postal_code"].widget.attrs.update(
            {"class": "form-control mb-2", "placeholder": _("postal code")}
        )
        self.fields["country"].widget.attrs.update({"class": "form-control mb-2"})
        self.fields["address_line2"].required = False
