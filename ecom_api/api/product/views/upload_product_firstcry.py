import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUploadFirstCry(CreateAPIView):
    serializer_class = ProductSerializerFirstCry

    def is_update(self, instance, data):

        if 'price' in data and data['price'] != instance.price.to_eng_string() if instance.price else "":
            LOGGER.info(f"Product price Updated from {instance.price} to {data['price']}!")
            return True


        elif 'name' in data and data['name'] != instance.name.to_eng_string() if instance.name else "":
            LOGGER.info(f"Product name Updated from {instance.name} to {data['name']}!")
            return True
        
        elif 'pid' in data and data['pid'] != instance.pid.to_eng_string() if instance.pid else "":
            LOGGER.info(f"Product pid Updated from {instance.pid} to {data['pid']}!")
            return True
        
        elif 'category' in data and data['category'] != instance.category.to_eng_string():
            LOGGER.info(f"Product category Updated from {instance.category} to {data['category']}!")
            return True
        
        elif 'rating' in data and data['rating'] != instance.rating.to_eng_string():
            LOGGER.info(f"Product rating Updated from {instance.rating} to {data['rating']}!")
            return True
        
        elif 'age' in data and data['age'] != instance.age:
            LOGGER.info(f"Product age Updated from {instance.age} to {data['age']}!")
            return True
        
        elif 'size' in data and data['size'] != instance.size:
            LOGGER.info(f"Product size Updated from {instance.size} to {data['size']}!")
            return True
        

        elif 'brand' in data and data['brand'] != instance.brand:
            LOGGER.info(f"Product brand Updated from {instance.brand} to {data['brand']}!")
            return True
        
        elif 'page' in data and data['page'] != instance.page:
            LOGGER.info(f"Product page Updated from {instance.page} to {data['page']}!")
            return True
        
        elif 'review' in data and data['review'] != instance.review:
            LOGGER.info(f"Product review Updated from {instance.review} to {data['review']}!")
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
            instance = Product_firstcry.objects.get(Q(id=data.get('id')) | Q(pid=data.get('pid')))
            if self.is_update(instance, data):
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.id}")
        except Product_firstcry.DoesNotExist:
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