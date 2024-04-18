from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from api.product.models import *
from api.product.serializers import *
from api.utils.choices import *
from distutils.util import strtobool


class CatalogueView(ListAPIView):

    def get_queryset(self):
        pass

    def get(self, request, *args, **kwargs):
        vendor_name = request.GET.get('vendor_name')
        short_scraper = bool(strtobool(request.GET.get('short_scraper', 'False')))
        if not vendor_name:
            print("No vendor_name")
            return Response({})

        vendor = Vendor.objects.filter(VendorName=vendor_name, is_active=True).first()
        if not vendor:
            print("No vendor")
            return Response({})
        
        categories = CategoryNameMapping.objects.filter(VendorCode=vendor, is_active=True)
        #print("Categories: ", categories)
        if short_scraper:
            categories = categories.filter(CategoryCode__CategoryName__in=SHORT_SCRAPER_CATEGORYNAMES)

        serializer = CategoryNameMappingSerializer(instance=categories, many=True)
        data = {
            'data': serializer.data,
            'VendorCode': vendor.VendorCode,
            'short_scraper': short_scraper
        }
        #print(data)
        return Response(data)
        
    
            

