from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from api.product.models import *
from api.product.serializers import *
from api.utils.choices import *
from distutils.util import strtobool


class ProductsView(ListAPIView):

    def get_queryset(self):
        pass

    def get(self, request, *args, **kwargs):
        vendor_name = request.GET.get('vendor_name')
        if not vendor_name:
            print("No vendor_name")
            return Response({})

        vendor = Vendor.objects.filter(VendorName=vendor_name, is_active=True).first()
        if not vendor:
            print("No vendor")
            return Response({})
        product_details = Product.objects.filter(VendorCode=vendor, is_active=True)\
            .select_related("CatalogueCode", "CategoryCode").values("URL", "SKU").order_by("DateInserted")

        # serializer = ProductSerializer(instance=product_details, many=True)
        data = {
            'product_details': product_details,
            # 'data': serializer.data,
            'VendorCode': vendor.VendorCode,
        }

        return Response(data)

