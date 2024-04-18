import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUploadEmax(CreateAPIView):
    serializer_class = ProductSerializerEmax

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
        
        elif 'sub_category' in data and data['sub_category'] != instance.sub_category:
            LOGGER.info(f"Product sub_category Updated from {instance.sub_category} to {data['sub_category']}!")
            return True

        elif 'in_stock' in data and data['in_stock'] != instance.in_stock:
            LOGGER.info(f"Product in_stock Updated from {instance.in_stock} to {data['in_stock']}!")
            return True
        
        elif 'brand' in data and data['brand'] != instance.brand:
            LOGGER.info(f"Product brand Updated from {instance.brand} to {data['brand']}!")
            return True
        
        elif 'description' in data and data['description'] != instance.description:
            LOGGER.info(f"Product description Updated from {instance.description} to {data['description']}!")
            return True
        
        elif 'product_id' in data and data['product_id'] != instance.product_id:
            LOGGER.info(f"Product product_id Updated from {instance.product_id} to {data['product_id']}!")
            return True
        
        elif 'sku' in data and data['sku'] != instance.sku:
            LOGGER.info(f"Product sku Updated from {instance.sku} to {data['sku']}!")
            return True

        elif 'color' in data and data['color'] != instance.color:
            LOGGER.info(f"Product color Updated from {instance.color} to {data['color']}!")
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
        
        elif 'percentage_discount' in data and float(data['percentage_discount']) != float(instance.percentage_discount):
            LOGGER.info(f"Product percentage_discount Updated from {instance.percentage_discount} to {data['percentage_discount']}!")
            return True

        else:
            return False



    def create(self, request, *args, **kwargs):
        print(type(request.data))
        print("###########################################")
        data = request.data.copy()  # This line should be inside the method
        try:
            instance = Product_Emax.objects.get(Q(id=data.get('id')) | Q(product_id=data.get('product_id')))
            if self.is_update(instance, data):
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.id}")
        except Product_Emax.DoesNotExist:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                LOGGER.info(f"Product Inserted: {instance.id}")

        return Response(data={
            'error': False,
            'message': 'Product added'
        })