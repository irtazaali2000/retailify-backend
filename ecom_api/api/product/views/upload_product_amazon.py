import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUploadAmazon(CreateAPIView):
    serializer_class = ProductSerializerAmazon

    def is_update(self, instance, data):

        if 'title' in data and data['title'] != instance.title:
            LOGGER.info(f"Product title Updated from {instance.title} to {data['title']}!")
            return True
        
        elif 'category' in data and data['category'] != instance.category:
            LOGGER.info(f"Product category Updated from {instance.category} to {data['category']}!")
            return True
        
        
        elif 'url' in data and data['url'] != instance.url:
            LOGGER.info(f"Product url Updated from {instance.url} to {data['url']}!")
            return True
        
        elif 'image' in data and data['image'] != instance.image:
            LOGGER.info(f"Product image Updated from {instance.image} to {data['image']}!")
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
        
        elif 'star_rating' in data and data['star_rating'] != instance.star_rating:
            LOGGER.info(f"Product star_rating Updated from {instance.star_rating} to {data['star_rating']}!")
            return True
        
        elif 'total_ratings' in data and data['total_ratings'] != instance.total_ratings:
            LOGGER.info(f"Product total_ratings Updated from {instance.total_ratings} to {data['total_ratings']}!")
            return True

        elif 'savings_perc' in data and data['savings_perc'] != instance.savings_perc:
            LOGGER.info(f"Product savings_perc Updated from {instance.savings_perc} to {data['savings_perc']}!")
            return True

        
        else:
            return False



    def create(self, request, *args, **kwargs):
        print(type(request.data))
        print("###########################################")
        data = request.data.copy()  # This line should be inside the method
        try:
            instance = Product_amazon.objects.get(Q(id=data.get('id')) | Q(url=data.get('url')))
            if self.is_update(instance, data):
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.id}")
        except Product_amazon.DoesNotExist:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                LOGGER.info(f"Product Inserted: {instance.id}")

        return Response(data={
            'error': False,
            'message': 'Product added'
        })