import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUploadMax(CreateAPIView):
    serializer_class = ProductSerializerMax

    def is_update(self, instance, data):

        if 'name' in data and data['name'] != instance.name:
            LOGGER.info(f"Product name Updated from {instance.name} to {data['name']}!")
            return True
        
        elif 'manufacturer_name' in data and data['manufacturer_name'] != instance.manufacturer_name:
            LOGGER.info(f"Product manufacturer_name Updated from {instance.manufacturer_name} to {data['manufacturer_name']}!")
            return True
        
        elif 'category' in data and data['category'] != instance.category:
            LOGGER.info(f"Product category Updated from {instance.category} to {data['category']}!")
            return True
        
        elif 'sub_categories' in data and data['sub_categories'] != instance.sub_categories:
            LOGGER.info(f"Product sub_categories Updated from {instance.sub_categories} to {data['sub_categories']}!")
            return True

        elif 'in_stock' in data and data['in_stock'] != instance.in_stock:
            LOGGER.info(f"Product in_stock Updated from {instance.in_stock} to {data['in_stock']}!")
            return True
        
        elif 'badge' in data and data['badge'] != instance.badge:
            LOGGER.info(f"Product badge Updated from {instance.badge} to {data['badge']}!")
            return True
        
        elif 'description' in data and data['description'] != instance.description:
            LOGGER.info(f"Product description Updated from {instance.description} to {data['description']}!")
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



    def create(self, request, *args, **kwargs):
        print(type(request.data))
        print("###########################################")
        data = request.data.copy()  # This line should be inside the method
        try:
            instance = Product_Max.objects.get(Q(id=data.get('id')) | Q(object_id=data.get('object_id')))
            if self.is_update(instance, data):
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.id}")
        except Product_Max.DoesNotExist:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                LOGGER.info(f"Product Inserted: {instance.id}")

        return Response(data={
            'error': False,
            'message': 'Product added'
        })