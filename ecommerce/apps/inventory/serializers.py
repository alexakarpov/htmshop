from rest_framework import serializers

from .models import ProductStock

class ProductStockSerializer(serializers.Serializer):
    product = serializers.CharField()
    product_type = serializers.CharField()
    
    sku = serializers.CharField()

    wrapping_qty = serializers.IntegerField()
    sanding_qty = serializers.IntegerField()
    painting_qty = serializers.IntegerField()
