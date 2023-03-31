from rest_framework import serializers

from .choice import ShippingChoice


class ShippingChoiceSerializer(serializers.Serializer):
    name = serializers.CharField()
    days = serializers.IntegerField()
    id = serializers.CharField()
    price = serializers.FloatField()


class OrderSerializer(serializers.Serializer):
    user = serializers.CharField()
    full_name = serializers.CharField()
    email = serializers.CharField()
    address1 = serializers.CharField()
    address2 = serializers.CharField()
    city = serializers.CharField()
    phone = serializers.CharField()
    postal_code = serializers.CharField()
    country_code = serializers.CharField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()
    total_paid = serializers.DecimalField(max_digits=5, decimal_places=2)
    order_key = serializers.CharField()
    payment_option = serializers.CharField()
    billing_status = serializers.BooleanField()
