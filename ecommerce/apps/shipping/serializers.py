from rest_framework import serializers

# from .choice import ShippingChoice


class ShippingChoiceSerializer(serializers.Serializer):
    name = serializers.CharField()
    days = serializers.IntegerField()
    id = serializers.CharField()
    price = serializers.FloatField()
