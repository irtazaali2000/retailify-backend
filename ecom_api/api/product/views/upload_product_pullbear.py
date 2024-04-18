import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUploadPullBear(CreateAPIView):
    serializer_class = ProductSerializerPullBear

    def is_update(self, instance, data):

        if 'name' in data and data['name'] != instance.name:
            LOGGER.info(f"Product name Updated from {instance.name} to {data['name']}!")
            return True
        
        elif 'category' in data and data['category'] != instance.category:
            LOGGER.info(f"Product category Updated from {instance.category} to {data['category']}!")
            return True
        
        elif 'sub_category' in data and data['sub_category'] != instance.sub_category:
            LOGGER.info(f"Product sub_category Updated from {instance.sub_category} to {data['sub_category']}!")
            return True
  
        elif 'description' in data and data['description'] != instance.description:
            LOGGER.info(f"Product description Updated from {instance.description} to {data['description']}!")
            return True 
        
        elif 'is_buyable' in data and data['is_buyable'] != instance.is_buyable:
            LOGGER.info(f"Product is_buyable Updated from {instance.is_buyable} to {data['is_buyable']}!")
            return True
        
        elif 'url' in data and data['url'] != instance.url:
            LOGGER.info(f"Product url Updated from {instance.url} to {data['url']}!")
            return True
        
        elif 'product_id' in data and data['product_id'] != instance.product_id:
            LOGGER.info(f"Product product_id Updated from {instance.product_id} to {data['product_id']}!")
            return True
        
        elif 'old_price_in_euro' in data and float(data['old_price_in_euro']) != float(instance.old_price_in_euro):
            LOGGER.info(f"Product old_price_in_euro Updated from {instance.old_price_in_euro} to {data['old_price_in_euro']}!")
            return True
        
        elif 'price_in_euro' in data and float(data['price_in_euro']) != float(instance.price_in_euro):
            LOGGER.info(f"Product price_in_euro Updated from {instance.price_in_euro} to {data['price_in_euro']}!")
            return True
        
        elif 'offset' in data and data['offset'] != instance.offset:
            LOGGER.info(f"Product offset Updated from {instance.offset} to {data['offset']}!")
            return True
        
        else:
            return False



    def create(self, request, *args, **kwargs):
        print(type(request.data))
        print("###########################################")
        data = request.data.copy()  # This line should be inside the method
        try:
            instance = Product_PullBear.objects.get(Q(id=data.get('id')) | Q(product_id=data.get('product_id')))
            if self.is_update(instance, data):
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.id}")
        except Product_PullBear.DoesNotExist:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                LOGGER.info(f"Product Inserted: {instance.id}")

        return Response(data={
            'error': False,
            'message': 'Product added'
        })