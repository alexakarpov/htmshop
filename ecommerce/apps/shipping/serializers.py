from rest_framework import serializers


class ShippingChoiceSESerializer(serializers.Serializer):
    name = serializers.CharField()
    days = serializers.IntegerField()
    id = serializers.CharField()
    price = serializers.FloatField()


class ShippingChoiceSSSerializer(serializers.Serializer):
    name = serializers.CharField()
    serviceCode = serializers.CharField()
    price = serializers.FloatField()
