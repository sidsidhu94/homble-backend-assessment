from rest_framework import serializers

from products.models import Product, Sku


class SkuSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sku
        fields = ["size", "selling_price"]


class ProductListSerializer(serializers.ModelSerializer):
    """
    To show list of products.
    """

    sku = serializers.SerializerMethodField()

    def get_sku(self, obj):

        sku_objects = obj.sku_set.all()
        sku_serializer = SkuSerializer(sku_objects, many=True)
        return sku_serializer.data

    class Meta:
        model = Product
        fields = ["name", "is_refrigerated", "ingredients", "sku"]
