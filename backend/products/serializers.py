from rest_framework import serializers
from .models import Product, VariantType, VariantOption, Combination

class VariantOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantOption
        fields = ['id', 'value']

class VariantTypeSerializer(serializers.ModelSerializer):
    options = VariantOptionSerializer(many=True, read_only=True)
    class Meta:
        model = VariantType
        fields = ['id', 'name', 'options']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'base_price']

class ProductDetailSerializer(serializers.ModelSerializer):
    variant_types = VariantTypeSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'base_price', 'variant_types']

class CombinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Combination
        fields = ['additional_price', 'stock']        
        
class CombinationListSerializer(serializers.ModelSerializer):
    options = VariantOptionSerializer(many=True, read_only=True)
    class Meta:
        model = Combination
        fields = ['id', 'options', 'additional_price', 'stock']        