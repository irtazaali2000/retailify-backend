import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUploadAsterPharmacy(CreateAPIView):
    serializer_class = ProductSerializerAsterPharmacy

    def is_update(self, instance, data):

        if 'title' in data and data['title'] != instance.title:
            LOGGER.info(f"Product title Updated from {instance.title} to {data['title']}!")
            return True
        
        elif 'category' in data and data['category'] != instance.category:
            LOGGER.info(f"Product category Updated from {instance.category} to {data['category']}!")
            return True
        
        elif 'matching_categories' in data and data['matching_categories'] != instance.matching_categories:
            LOGGER.info(f"Product matching_categories Updated from {instance.matching_categories} to {data['matching_categories']}!")
            return True
  
        elif 'brand' in data and data['brand'] != instance.brand:
            LOGGER.info(f"Product brand Updated from {instance.brand} to {data['brand']}!")
            return True
        
        
        elif 'sku' in data and data['sku'] != instance.sku:
            LOGGER.info(f"Product sku Updated from {instance.sku} to {data['sku']}!")
            return True

        
        elif 'url' in data and data['url'] != instance.url:
            LOGGER.info(f"Product url Updated from {instance.url} to {data['url']}!")
            return True
        
        elif 'img' in data and data['img'] != instance.img:
            LOGGER.info(f"Product img Updated from {instance.img} to {data['img']}!")
            return True
        

        elif 'offer_price_in_aed' in data and float(data['offer_price_in_aed']) != float(instance.offer_price_in_aed):
            LOGGER.info(f"Product offer_price_in_aed Updated from {instance.offer_price_in_aed} to {data['offer_price_in_aed']}!")
            return True
        
        elif 'price_in_aed' in data and float(data['price_in_aed']) != float(instance.price_in_aed):
            LOGGER.info(f"Product price_in_aed Updated from {instance.price_in_aed} to {data['price_in_aed']}!")
            return True
        
        elif 'page' in data and data['page'] != instance.page:
            LOGGER.info(f"Product page Updated from {instance.page} to {data['page']}!")
            return True
        
        elif 'quantity' in data and data['quantity'] != instance.quantity:
            LOGGER.info(f"Product quantity Updated from {instance.quantity} to {data['quantity']}!")
            return True
        
        elif 'rating' in data and float(data['rating']) != float(instance.rating):
            LOGGER.info(f"Product rating Updated from {instance.rating} to {data['rating']}!")
            return True
        
        elif 'in_stock' in data and data['in_stock'] != instance.in_stock:
            LOGGER.info(f"Product in_stock Updated from {instance.in_stock} to {data['in_stock']}!")
            return True
        
        else:
            return False



    def create(self, request, *args, **kwargs):
        print(type(request.data))
        print("###########################################")
        data = request.data.copy()  # This line should be inside the method
        try:
            instance = Product_AsterPharmacy.objects.get(Q(id=data.get('id')) | Q(sku=data.get('sku')))
            if self.is_update(instance, data):
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.id}")
        except Product_AsterPharmacy.DoesNotExist:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                LOGGER.info(f"Product Inserted: {instance.id}")

        return Response(data={
            'error': False,
            'message': 'Product added'
        })