from rest_framework import serializers

from .models import Stock

class ProductStockSerializer(serializers.Serializer):
    product = serializers.CharField()
    sku = serializers.CharField()
    wrapping_qty = serializers.IntegerField()
    sanding_qty = serializers.IntegerField()
    painting_qty = serializers.IntegerField()
