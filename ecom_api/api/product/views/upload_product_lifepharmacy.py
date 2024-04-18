import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUploadLifePharmacy(CreateAPIView):
    serializer_class = ProductSerializerLifePharmacy

    def is_update(self, instance, data):

        if 'title' in data and data['title'] != instance.title:
            LOGGER.info(f"Product title Updated from {instance.title} to {data['title']}!")
            return True
        
        elif 'category' in data and data['category'] != instance.category:
            LOGGER.info(f"Product category Updated from {instance.category} to {data['category']}!")
            return True
        
        elif 'sub_category' in data and data['sub_category'] != instance.sub_category:
            LOGGER.info(f"Product sub_category Updated from {instance.sub_category} to {data['sub_category']}!")
            return True
  
        elif 'brand' in data and data['brand'] != instance.brand:
            LOGGER.info(f"Product brand Updated from {instance.brand} to {data['brand']}!")
            return True
        
        elif 'description' in data and data['description'] != instance.description:
            LOGGER.info(f"Product description Updated from {instance.description} to {data['description']}!")
            return True
        
        elif 'sku' in data and data['sku'] != instance.sku:
            LOGGER.info(f"Product sku Updated from {instance.sku} to {data['sku']}!")
            return True

        elif 'tax_rate' in data and data['tax_rate'] != instance.tax_rate:
            LOGGER.info(f"Product tax_rate Updated from {instance.tax_rate} to {data['tax_rate']}!")
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
        
        elif 'regular_price_in_aed' in data and float(data['regular_price_in_aed']) != float(instance.regular_price_in_aed):
            LOGGER.info(f"Product regular_price_in_aed Updated from {instance.regular_price_in_aed} to {data['regular_price_in_aed']}!")
            return True
        
        elif 'page' in data and data['page'] != instance.page:
            LOGGER.info(f"Product page Updated from {instance.page} to {data['page']}!")
            return True
        
        elif 'max_salable_qty' in data and data['max_salable_qty'] != instance.max_salable_qty:
            LOGGER.info(f"Product max_salable_qty Updated from {instance.max_salable_qty} to {data['max_salable_qty']}!")
            return True
        
        elif 'rating' in data and float(data['rating']) != float(instance.rating):
            LOGGER.info(f"Product rating Updated from {instance.rating} to {data['rating']}!")
            return True
        
        elif 'out_of_stock' in data and data['out_of_stock'] != instance.out_of_stock:
            LOGGER.info(f"Product out_of_stock Updated from {instance.out_of_stock} to {data['out_of_stock']}!")
            return True
        
        elif 'active' in data and data['active'] != instance.active:
            LOGGER.info(f"Product active Updated from {instance.active} to {data['active']}!")
            return True

        else:
            return False



    def create(self, request, *args, **kwargs):
        print(type(request.data))
        print("###########################################")
        data = request.data.copy()  # This line should be inside the method
        try:
            instance = Product_LifePharmacy.objects.get(Q(id=data.get('id')) | Q(sku=data.get('sku')))
            if self.is_update(instance, data):
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.id}")
        except Product_LifePharmacy.DoesNotExist:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                LOGGER.info(f"Product Inserted: {instance.id}")

        return Response(data={
            'error': False,
            'message': 'Product added'
        })