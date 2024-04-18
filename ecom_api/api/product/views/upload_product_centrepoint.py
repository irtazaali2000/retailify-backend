import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUploadCentrePoint(CreateAPIView):
    serializer_class = ProductSerializerCentrePoint

    def is_update(self, instance, data):

        if 'name' in data and data['name'] != instance.name:
            LOGGER.info(f"Product name Updated from {instance.name} to {data['name']}!")
            return True
        
        elif 'category' in data and data['category'] != instance.category:
            LOGGER.info(f"Product category Updated from {instance.category} to {data['category']}!")
            return True
        
        elif 'sub_categories' in data and data['sub_categories'] != instance.sub_categories:
            LOGGER.info(f"Product sub_categories Updated from {instance.sub_categories} to {data['sub_categories']}!")
            return True
        
        elif 'object_id' in data and data['object_id'] != instance.object_id:
            LOGGER.info(f"Product object_id Updated from {instance.object_id} to {data['object_id']}!")
            return True
        
        elif 'url' in data and data['url'] != instance.url:
            LOGGER.info(f"Product url Updated from {instance.url} to {data['url']}!")
            return True
        
        elif 'img' in data and data['img'] != instance.img:
            LOGGER.info(f"Product img Updated from {instance.img} to {data['img']}!")
            return True
        

        elif 'price_in_aed' in data and data['price_in_aed'] != instance.price_in_aed.to_eng_string():
            LOGGER.info(f"Product price_in_aed Updated from {instance.price_in_aed} to {data['price_in_aed']}!")
            return True
        
        elif 'old_price_in_aed' in data and data['old_price_in_aed'] != instance.old_price_in_aed.to_eng_string():
            LOGGER.info(f"Product old_price_in_aed Updated from {instance.old_price_in_aed} to {data['old_price_in_aed']}!")
            return True
        
        elif 'page' in data and data['page'] != instance.page:
            LOGGER.info(f"Product page Updated from {instance.page} to {data['page']}!")
            return True
        
        elif 'rating' in data and data['rating'] != instance.rating.to_eng_string():
            LOGGER.info(f"Product rating Updated from {instance.rating} to {data['rating']}!")
            return True

        else:
            return False


    # def is_review_count_updated(self, instance, data):
    #     if 'ReviewCount' in data and data['ReviewCount'] != instance.ReviewCount:
    #         return True
    #     else:
    #         return False


    def create(self, request, *args, **kwargs):
        print(type(request.data))
        print("###########################################")
        data = request.data.copy()  # This line should be inside the method
        try:
            instance = Product_CentrePoint.objects.get(Q(id=data.get('id')) | Q(object_id=data.get('object_id')))
            if self.is_update(instance, data):
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.id}")
        except Product_CentrePoint.DoesNotExist:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                LOGGER.info(f"Product Inserted: {instance.id}")

        return Response(data={
            'error': False,
            'message': 'Product added'
        })



# class StockAvailabilityUpdate(CreateAPIView):
#     serializer_class = StockAvailabilitySerializer

#     def create(self, request, *args, **kwargs):
#         data = request.data.copy()
#         StockAvailability = data.pop('StockAvailability')
#         instance = Product.objects.get(Q(SKU=data.get('SKU')) | Q(URL=data.get('URL')))
#         if instance:
#             if instance.StockAvailability == StockAvailability:
#                 print(f"StockAvailability Upto Date | {data.get('URL')}")
#                 return Response(data={
#                     'success': True,
#                     'message': 'StockAvailability Upto Date!'
#                 })
#             print(f"StockAvailability Updated from: "
#                   f"{instance.StockAvailability} to {StockAvailability} | {data.get('URL')}")
#             instance.StockAvailability = StockAvailability
#             instance.save()
#             return Response(data={
#                 'success': True,
#                 'message': 'StockAvailability Updated!'
#             })
#         return Response(data={
#             'success': False,
#             'message': 'Product Not Found!'
#         })
    

# class StockAvailabilityUpdate(CreateAPIView):
#     serializer_class = ProductSerializerCarrefour

#     def create(self, request, *args, **kwargs):
#         data = request.data.copy()
#         stock_availability = data.pop('availability')

#         try:
#             product = Product_carrefour.objects.get(Q(SKU=data.get('product_id')) | Q(URL=data.get('URL')))
#             product.availability = stock_availability
#             product.save()

#             serializer = self.get_serializer(product)

#             return Response(data={
#                 'success': True,
#                 'message': 'StockAvailability Updated!',
#                 'data': serializer.data,
#             })

#         except Product_carrefour.DoesNotExist:
#             return Response(data={
#                 'success': False,
#                 'message': 'Product Not Found!'
#             }, status=status.HTTP_404_NOT_FOUND)