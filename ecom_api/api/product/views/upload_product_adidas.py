import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUploadAdidas(CreateAPIView):
    serializer_class = ProductSerializerAdidas

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
  
        elif 'model_id' in data and data['model_id'] != instance.model_id:
            LOGGER.info(f"Product model_id Updated from {instance.model_id} to {data['model_id']}!")
            return True 
        
        elif 'url' in data and data['url'] != instance.url:
            LOGGER.info(f"Product url Updated from {instance.url} to {data['url']}!")
            return True
        
        elif 'img' in data and data['img'] != instance.img:
            LOGGER.info(f"Product img Updated from {instance.img} to {data['img']}!")
            return True
        
        elif 'sale_price_in_dollars' in data and float(data['sale_price_in_dollars']) != float(instance.sale_price_in_dollars):
            LOGGER.info(f"Product sale_price_in_dollars Updated from {instance.sale_price_in_dollars} to {data['sale_price_in_dollars']}!")
            return True
        
        elif 'price_in_dollars' in data and float(data['price_in_dollars']) != float(instance.price_in_dollars):
            LOGGER.info(f"Product price_in_dollars Updated from {instance.price_in_dollars} to {data['price_in_dollars']}!")
            return True
        
        elif 'page' in data and data['page'] != instance.page:
            LOGGER.info(f"Product page Updated from {instance.page} to {data['page']}!")
            return True
        
        elif 'sale_percentage' in data and data['sale_percentage'] != instance.sale_percentage:
            LOGGER.info(f"Product sale_percentage Updated from {instance.sale_percentage} to {data['sale_percentage']}!")
            return True
        
        elif 'rating' in data and float(data['rating']) != float(instance.rating):
            LOGGER.info(f"Product rating Updated from {instance.rating} to {data['rating']}!")
            return True
        
        elif 'review' in data and data['review'] != instance.review:
            LOGGER.info(f"Product review Updated from {instance.review} to {data['review']}!")
            return True
        
        elif 'orderable' in data and data['orderable'] != instance.orderable:
            LOGGER.info(f"Product orderable Updated from {instance.orderable} to {data['orderable']}!")
            return True
        
        
        else:
            return False



    def create(self, request, *args, **kwargs):
        print(type(request.data))
        print("###########################################")
        data = request.data.copy()  # This line should be inside the method
        try:
            instance = Product_Adidas.objects.get(Q(id=data.get('id')) | Q(model_id=data.get('model_id')))
            if self.is_update(instance, data):
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.id}")
        except Product_Adidas.DoesNotExist:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                LOGGER.info(f"Product Inserted: {instance.id}")

        return Response(data={
            'error': False,
            'message': 'Product added'
        })