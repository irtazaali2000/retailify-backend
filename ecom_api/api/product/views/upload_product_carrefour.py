import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUploadCarrefour(CreateAPIView):
    serializer_class = ProductSerializerCarrefour

    def is_update(self, instance, data):
        if 'StockAvailability' in data and data['StockAvailability'] != instance.StockAvailability:
            LOGGER.info(f"Product availabilty Updated {instance.StockAvailability} to {data['StockAvailability']}!")
            return True
        # elif not instance.Offer and 'Offer' in data and float(data['Offer']):
        #     LOGGER.info(f"Product Offer Updated from {instance.Offer} to {data['Offer']}!")
        #     return True
        # elif 'Offer' in data and float(data['Offer']) and data['Offer'] != instance.Offer.to_eng_string() if instance.Offer else "":
        #     LOGGER.info(f"Product Offer Updated from {instance.Offer} to {data['Offer']}!")
        #     return True
        elif 'RegularPrice' in data and data['RegularPrice'] != instance.RegularPrice.to_eng_string() if instance.RegularPrice else "":
            LOGGER.info(f"Product RegularPrice Updated from {instance.RegularPrice} to {data['RegularPrice']}!")
            return True
        # elif 'RatingValue' in data and "{:.2f}".format(data['RatingValue']) != instance.RatingValue.to_eng_string():
        #     LOGGER.info(f"Product RatingValue Updated from {instance.RatingValue} to {'{:.2f}'.format(data['RatingValue'])}!")
        #     return True
        # elif 'BestRating' in data and "{:.2f}".format(data['BestRating']) != instance.BestRating.to_eng_string():
        #     LOGGER.info(f"Product BestRating Updated from {instance.BestRating} to {'{:.2f}'.format(data['BestRating'])}!")
        #     return True
        # elif 'ReviewCount' in data and data['ReviewCount'] != instance.ReviewCount:
        #     LOGGER.info(f"Product ReviewCount Updated from {instance.ReviewCount} to {data['ReviewCount']}!")
        #     return True
        else:
            return False


    def is_review_count_updated(self, instance, data):
        if 'ReviewCount' in data and data['ReviewCount'] != instance.ReviewCount:
            return True
        else:
            return False


    def create(self, request, *args, **kwargs):
        print(type(request.data))
        print("###########################################")
        data = request.data.copy()  # This line should be inside the method
        try:
            instance = Product_carrefour.objects.get(Q(ProductId=data.get('product_id')) | Q(URL=data.get('URL')))
            if self.is_update(instance, data):
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.ProductCode}")
        except Product_carrefour.DoesNotExist:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                LOGGER.info(f"Product Inserted: {instance.ProductCode}")

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
    

class StockAvailabilityUpdate(CreateAPIView):
    serializer_class = ProductSerializerCarrefour

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        stock_availability = data.pop('availability')

        try:
            product = Product_carrefour.objects.get(Q(SKU=data.get('product_id')) | Q(URL=data.get('URL')))
            product.availability = stock_availability
            product.save()

            serializer = self.get_serializer(product)

            return Response(data={
                'success': True,
                'message': 'StockAvailability Updated!',
                'data': serializer.data,
            })

        except Product_carrefour.DoesNotExist:
            return Response(data={
                'success': False,
                'message': 'Product Not Found!'
            }, status=status.HTTP_404_NOT_FOUND)