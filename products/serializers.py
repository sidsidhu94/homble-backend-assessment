from rest_framework import serializers

from products.models import Product, Sku


class SkuCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Sku instances.
    """

    def validate(self, data):
        product = data["product"]
        size = data["size"]
        if Sku.objects.filter(product=product, size=size).exists():
            raise serializers.ValidationError(
                "A Sku with the same size for this product already exists."
            )
        return data

    class Meta:
        model = Sku
        fields = [
            "product",
            "size",
            "measurement_unit",
            "platform_commission",
            "cost_price",
        ]


class SkuSerializer(serializers.ModelSerializer):

    markup_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Sku
        fields = ["size", "selling_price", "markup_percentage"]

    def get_markup_percentage(self, obj):
        if obj.cost_price:
            return (obj.platform_commission / obj.cost_price) * 100

        return None


class ProductListSerializer(serializers.ModelSerializer):
    """
    To show list of products.
    """

    sku = serializers.SerializerMethodField()

    def get_sku(self, obj):

        sku_objects = obj.sku_set.filter(status=1)
        sku_serializer = SkuSerializer(sku_objects, many=True)
        return sku_serializer.data

    class Meta:
        model = Product
        fields = ["name", "is_refrigerated", "ingredients", "sku"]


class SkuListSerializer(serializers.ModelSerializer):
    """
    To show list of sku with category.
    """

    category = serializers.StringRelatedField(source="product.category")
    product = ProductListSerializer()

    class Meta:
        model = Sku
        fields = ["product", "size", "selling_price", "category"]
