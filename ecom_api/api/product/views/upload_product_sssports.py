import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUploadSunAndSandSports(CreateAPIView):
    serializer_class = ProductSerializerSunAndSandSports

    def is_update(self, instance, data):

        if 'title' in data and data['title'] != instance.title:
            LOGGER.info(f"Product title Updated from {instance.title} to {data['title']}!")
            return True
        
        elif 'category' in data and data['category'] != instance.category:
            LOGGER.info(f"Product category Updated from {instance.category} to {data['category']}!")
            return True
        
        elif 'type' in data and data['type'] != instance.type:
            LOGGER.info(f"Product type Updated from {instance.type} to {data['type']}!")
            return True
  
        elif 'brand' in data and data['brand'] != instance.brand:
            LOGGER.info(f"Product brand Updated from {instance.brand} to {data['brand']}!")
            return True 
        
        elif 'product_code' in data and data['product_code'] != instance.product_code:
            LOGGER.info(f"Product product_code Updated from {instance.product_code} to {data['product_code']}!")
            return True
        
        elif 'url' in data and data['url'] != instance.url:
            LOGGER.info(f"Product url Updated from {instance.url} to {data['url']}!")
            return True
        
        elif 'img' in data and data['img'] != instance.img:
            LOGGER.info(f"Product img Updated from {instance.img} to {data['img']}!")
            return True
        
        elif 'price_in_aed' in data and float(data['price_in_aed']) != float(instance.price_in_aed):
            LOGGER.info(f"Product price_in_aed Updated from {instance.price_in_aed} to {data['price_in_aed']}!")
            return True
        
        elif 'old_price_in_aed' in data and float(data['old_price_in_aed']) != float(instance.old_price_in_aed):
            LOGGER.info(f"Product old_price_in_aed Updated from {instance.old_price_in_aed} to {data['old_price_in_aed']}!")
            return True
        
        elif 'page' in data and data['page'] != instance.page:
            LOGGER.info(f"Product page Updated from {instance.page} to {data['page']}!")
            return True
        
        elif 'description' in data and data['description'] != instance.description:
            LOGGER.info(f"Product description Updated from {instance.description} to {data['description']}!")
            return True
        
        elif 'product_elements' in data and data['product_elements'] != instance.product_elements:
            LOGGER.info(f"Product product_elements Updated from {instance.product_elements} to {data['product_elements']}!")
            return True
        
        elif 'discount' in data and data['discount'] != instance.discount:
            LOGGER.info(f"Product discount Updated from {instance.discount} to {data['discount']}!")
            return True

        elif 'is_limited_stock' in data and data['is_limited_stock'] != instance.is_limited_stock:
            LOGGER.info(f"Product is_limited_stock Updated from {instance.is_limited_stock} to {data['is_limited_stock']}!")
            return True
        
        else:
            return False



    def create(self, request, *args, **kwargs):
        print(type(request.data))
        print("###########################################")
        data = request.data.copy()  # This line should be inside the method
        try:
            instance = Product_SunAndSandSports.objects.get(Q(id=data.get('id')) | Q(product_code=data.get('product_code')))
            if self.is_update(instance, data):
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.id}")
        except Product_SunAndSandSports.DoesNotExist:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                LOGGER.info(f"Product Inserted: {instance.id}")

        return Response(data={
            'error': False,
            'message': 'Product added'
        })