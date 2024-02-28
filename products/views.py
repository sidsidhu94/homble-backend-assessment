from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_405_METHOD_NOT_ALLOWED,
)

from .models import Product, Sku
from .serializers import ProductListSerializer, SkuCreateSerializer

from rest_framework.permissions import BasePermission


class SkuEditPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(
            name="Supervisors"
        ).exists() or request.user.has_perm("products.change_sku")


@api_view(["GET"])
@permission_classes([AllowAny])
def products_list(request):
    """
    List of all products.Handling the refrigerated products based on the query parameter "true" or "false" or no query passed
    """
    refrigerated_products = request.query_params.get("refrigerated")

    if refrigerated_products == "true":
        products = Product.objects.filter(is_refrigerated=True)

    elif refrigerated_products == "false":
        products = Product.objects.filter(is_refrigerated=False)
    else:
        products = Product.objects.all()

    serializer = ProductListSerializer(products, many=True)
    return Response({"products": serializer.data}, status=HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_sku(request):
    data = request.data.copy()
    print(data)

    if "cost_price" not in data or "platform_commission" not in data:
        return Response(
            {"error": "cost_price and platform_commission are required fields"},
            status=HTTP_400_BAD_REQUEST,
        )

    serializer = SkuCreateSerializer(data=data)
    if serializer.is_valid():

        sku = serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(status=HTTP_404_NOT_FOUND)

    skus = product.sku_set.filter(status=1)

    product_serializer = ProductListSerializer(product)

    product_data = product_serializer.data

    return Response({"products": product_data}, status=HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([SkuEditPermission])
def edit_sku_status(request, sku_id):
    try:
        sku = Sku.objects.get(id=sku_id)
    except Sku.DoesNotExist:
        return JsonResponse({"error": "Sku not found"}, status=HTTP_404_NOT_FOUND)

    if request.method == "PATCH":
        status_value = request.data.get("status")
        if status_value is not None:
            sku.status = status_value
            sku.save()
            return JsonResponse(
                {"message": "Sku status updated successfully"}, status=HTTP_200_OK
            )
        else:
            return JsonResponse(
                {"error": "Status value not provided"}, status=HTTP_400_BAD_REQUEST
            )

    return JsonResponse(
        {"error": "Invalid request method"}, status=HTTP_405_METHOD_NOT_ALLOWED
    )
