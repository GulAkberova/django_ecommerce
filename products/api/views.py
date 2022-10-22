from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .serializers import ProductSerializer
from products.models import Product


@api_view(['GET'])
def product_list_view(request):
    if request.method == 'GET':
        products = Product.objects.order_by("created_at")
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


@api_view(["GET", "DELETE", "PUT"])
def product_detail_view(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    if request.method == "DELETE":
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if request.method == "PUT":
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
