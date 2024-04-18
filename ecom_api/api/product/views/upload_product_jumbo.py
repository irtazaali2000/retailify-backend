import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUploadJumbo(CreateAPIView):
    serializer_class = ProductSerializerJumbo

    def is_update(self, instance, data):
        # if 'StockAvailability' in data and data['StockAvailability'] != instance.StockAvailability:
        #     LOGGER.info(f"Product availabilty Updated {instance.StockAvailability} to {data['StockAvailability']}!")
        #     return True
        # elif not instance.Offer and 'Offer' in data and float(data['Offer']):
        #     LOGGER.info(f"Product Offer Updated from {instance.Offer} to {data['Offer']}!")
        #     return True
        # elif 'Offer' in data and float(data['Offer']) and data['Offer'] != instance.Offer.to_eng_string() if instance.Offer else "":
        #     LOGGER.info(f"Product Offer Updated from {instance.Offer} to {data['Offer']}!")
        #     return True
        if 'price' in data and data['price'] != instance.price.to_eng_string() if instance.price else "":
            LOGGER.info(f"Product price Updated from {instance.price} to {data['price']}!")
            return True


        if 'name' in data and data['name'] != instance.name.to_eng_string() if instance.name else "":
            LOGGER.info(f"Product name Updated from {instance.name} to {data['name']}!")
            return True
        
        if 'url' in data and data['url'] != instance.url.to_eng_string() if instance.url else "":
            LOGGER.info(f"Product url Updated from {instance.url} to {data['url']}!")
            return True
        
        elif 'categories' in data and data['categories'] != instance.categories.to_eng_string():
            LOGGER.info(f"Product categories Updated from {instance.categories} to {data['categories']}!")
            return True
        
        elif 'img_url' in data and data['img_url'] != instance.img_url.to_eng_string():
            LOGGER.info(f"Product img_url Updated from {instance.img_url} to {data['img_url']}!")
            return True
        
        elif 'in_stock' in data and data['in_stock'] != instance.in_stock:
            LOGGER.info(f"Product in_stock Updated from {instance.in_stock} to {data['in_stock']}!")
            return True
        
        elif 'sku' in data and data['sku'] != instance.sku:
            LOGGER.info(f"Product sku Updated from {instance.sku} to {data['sku']}!")
            return True
        

        elif 'in_stock' in data and data['in_stock'] != instance.in_stock:
            LOGGER.info(f"Product in_stock Updated from {instance.in_stock} to {data['in_stock']}!")
            return True
        

        elif 'item_number' in data and data['item_number'] != instance.item_number:
            LOGGER.info(f"Product item_number Updated from {instance.item_number} to {data['item_number']}!")
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
            instance = Product_jumbo.objects.get(Q(id=data.get('id')) | Q(url=data.get('url')))
            if self.is_update(instance, data):
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.id}")
        except Product_jumbo.DoesNotExist:
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