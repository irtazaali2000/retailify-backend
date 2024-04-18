import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUploadHandM(CreateAPIView):
    serializer_class = ProductSerializerHandM

    def is_update(self, instance, data):

        if 'title' in data and data['title'] != instance.title:
            LOGGER.info(f"Product title Updated from {instance.title} to {data['title']}!")
            return True
        
        elif 'main_category' in data and data['main_category'] != instance.main_category:
            LOGGER.info(f"Product main_category Updated from {instance.main_category} to {data['main_category']}!")
            return True
        
        elif 'sub_category' in data and data['sub_category'] != instance.sub_category:
            LOGGER.info(f"Product sub_category Updated from {instance.sub_category} to {data['sub_category']}!")
            return True
        
        elif 'article_code' in data and data['article_code'] != instance.article_code:
            LOGGER.info(f"Product article_code Updated from {instance.article_code} to {data['article_code']}!")
            return True
        
        elif 'url' in data and data['url'] != instance.url:
            LOGGER.info(f"Product url Updated from {instance.url} to {data['url']}!")
            return True
        
        elif 'img' in data and data['img'] != instance.img:
            LOGGER.info(f"Product img Updated from {instance.img} to {data['img']}!")
            return True
        

        elif 'price_in_dollars' in data and data['price_in_dollars'] != instance.price_in_dollars.to_eng_string():
            LOGGER.info(f"Product price_in_dollars Updated from {instance.price_in_dollars} to {data['price_in_dollars']}!")
            return True
        
        elif 'discounted_price_in_dollars' in data and data['discounted_price_in_dollars'] != instance.discounted_price_in_dollars.to_eng_string():
            LOGGER.info(f"Product discounted_price_in_dollars Updated from {instance.discounted_price_in_dollars} to {data['discounted_price_in_dollars']}!")
            return True
        
        elif 'selling_attribute' in data and data['selling_attribute'] != instance.selling_attribute:
            LOGGER.info(f"Product selling_attribute Updated from {instance.selling_attribute} to {data['selling_attribute']}!")
            return True
        
        elif 'brand' in data and data['brand'] != instance.brand:
            LOGGER.info(f"Product brand Updated from {instance.brand} to {data['brand']}!")
            return True
        
        elif 'page' in data and data['page'] != instance.page:
            LOGGER.info(f"Product page Updated from {instance.page} to {data['page']}!")
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
            instance = Product_HandM.objects.get(Q(id=data.get('id')) | Q(article_code=data.get('article_code')))
            if self.is_update(instance, data):
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.id}")
        except Product_HandM.DoesNotExist:
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