import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUpload(CreateAPIView):
    serializer_class = ProductSerializer

    def is_update(self, instance, data):
        if 'StockAvailability' in data and data['StockAvailability'] != instance.StockAvailability:
            LOGGER.info(f"Product availabilty Updated {instance.StockAvailability} to {data['StockAvailability']}!")
            return True
        # elif not instance.Offer and 'Offer' in data and float(data['Offer']):
        #     LOGGER.info(f"Product Offer Updated from {instance.Offer} to {data['Offer']}!")
        #     return True
        elif 'Offer' in data and float(data['Offer'])!= float(instance.Offer):
            LOGGER.info(f"Product Offer Updated from {instance.Offer} to {data['Offer']}!")
            return True
        elif 'RegularPrice' in data and float(data['RegularPrice']) != float(instance.RegularPrice):
            LOGGER.info(f"Product RegularPrice Updated from {instance.RegularPrice} to {data['RegularPrice']}!")
            return True
        elif 'RatingValue' in data and float(data['RatingValue']) != float(instance.RatingValue):
            LOGGER.info(f"Product RatingValue Updated from {instance.RatingValue} to {data['RatingValue']}!")
            return True
        elif 'BestRating' in data and float(data['BestRating']) != float(instance.BestRating):
            LOGGER.info(f"Product BestRating Updated from {instance.BestRating} to {data['BestRating']}!")
            return True
        elif 'ReviewCount' in data and data['ReviewCount'] != instance.ReviewCount:
            LOGGER.info(f"Product ReviewCount Updated from {instance.ReviewCount} to {data['ReviewCount']}!")
            return True
        else:
            return False


    def is_review_count_updated(self, instance, data):
        if 'ReviewCount' in data and data['ReviewCount'] != instance.ReviewCount:
            return True
        else:
            return False


    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        image = data.pop('MainImage')
        additional_properties = data.pop('AdditionalProperty', [])
        reviews = data.pop('reviews', [])
        #rating = data.pop('Rating', {})
        is_exist = False
        is_review_count_updated = False
        try:
            instance = Product.objects.get(Q(SKU=data.get('SKU')) | Q(URL=data.get('URL')))
            is_exist = True
            if self.is_review_count_updated(instance, data):
                is_review_count_updated = True

            if self.is_update(instance, data):
                if not data['StockAvailability']:
                    data['RegularPrice'] = instance.RegularPrice
                    data['Offer'] = instance.Offer
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.SKU}")

        except Product.DoesNotExist:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                LOGGER.info(f"Product Inserted: {instance.SKU}")

        if not is_exist:
            #for image in images:
            if 'MainImage' in image and image['MainImage']:
                img_serializer = ImageSerializer(data={
                    'ProductCode': instance.ProductCode,
                    'SKU': instance.SKU,
                    'image_url': instance.MainImage
                })
                if img_serializer.is_valid(raise_exception=True):
                    img_serializer.save()

                LOGGER.info(f"Product Images Inserted: {instance.SKU}")
                
            if additional_properties:
                ap_serializer = AdditionalPropertiesSerializer(data={
                    'ProductCode': instance.ProductCode,
                    'SKU': instance.SKU,
                    'AdditionalProperty': json.dumps(additional_properties)
                })
                if ap_serializer.is_valid(raise_exception=True):
                    ap_serializer.save()
                LOGGER.info(f"Product AdditionalProperty Inserted: {instance.SKU}")

            category_name_mapping_exists = CategoryNameMapping.objects.filter(
                VendorCode=instance.VendorCode.VendorCode,
                CategoryCode=instance.CategoryCode.CategoryCode
            ).exists()

            if not category_name_mapping_exists:
                category_name_mapping_serializer = CategoryNameMappingSerializer(data={
                    'VendorCode': instance.VendorCode.VendorCode,  # Pass Vendor primary key
                    'CategoryCode': instance.CategoryCode.CategoryCode,  # Pass Category primary key
                    'CategoryName': instance.CategoryName
                })

                if category_name_mapping_serializer.is_valid(raise_exception=True):
                    category_name_mapping_serializer.save()

                LOGGER.info(f"Product CategoryNameMapping Inserted: {instance.SKU}")
            else:
                LOGGER.info(f"CategoryNameMapping already exists for Product: {instance.SKU}")

            # for review_data in reviews:
        if reviews:
            for review_data in reviews:
                if 'Comment' in review_data and review_data['Comment']:
                    # Check if a review with the same comment, comment date, and source already exists
                    existing_reviews = Review.objects.filter(Comment=review_data['Comment'], 
                                            CommentDate=review_data['CommentDate'],
                                            Source=review_data['Source'])

                    if existing_reviews.exists():
                        pass
                        #LOGGER.warning(f"Duplicate review not inserted!")
                    else:
                        # If no review with the same attributes exists, proceed with insertion
                        review_serializer = ReviewSerializer(data={
                            'ProductCode': instance.ProductCode,
                            'SKU': instance.SKU,
                            'Comment': review_data['Comment'],
                            'Source': review_data['Source'],
                            'CommentDate': review_data['CommentDate'],
                            'rating': review_data['rating'],
                            'max_rating': review_data['max_rating'],
                            'average_rating': review_data['average_rating']
                        })

                        if review_serializer.is_valid():
                            review_serializer.save()
                            LOGGER.info(f"Product Review Inserted: {instance.SKU}")
                        else:
                            LOGGER.error(f"Review Serializer Errors: {review_serializer.errors}")



            # for review in reviews:
            #     review['ProductCode'] = instance.ProductCode
            #     review['SKU'] = instance.SKU
            #     try:
            #         Review.objects.get(
            #             SKU=instance.SKU
            #         )
            #     except Review.DoesNotExist:
            #         review_serializer = ReviewSerializer(data=review)
            #         if review_serializer.is_valid(raise_exception=True):
            #             review_serializer.save()
            #             LOGGER.info(f"Product Review Inserted: {instance.SKU}")


        # if rating:
        #     rating['ProductCode'] = instance.ProductCode
        #     rating['SKU'] = instance.SKU
        #     try:
        #         instance = Rating.objects.get(ProductCode=instance.ProductCode, SKU=instance.SKU)
        #         if is_review_count_updated:
        #             rating_serializer = RatingSerializer(instance=instance, data=rating)
        #             if rating_serializer.is_valid(raise_exception=True):
        #                 rating_serializer.save()
        #                 LOGGER.info(f"Product Rating Updated: {instance.SKU}")

        #     except Rating.DoesNotExist:
        #         rating_serializer = RatingSerializer(data=rating)

        #         if rating_serializer.is_valid(raise_exception=True):
        #             rating_serializer.save()
        #             LOGGER.info(f"Product Rating Inserted: {instance.SKU}")

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
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        stock_availability = data.pop('StockAvailability')

        try:
            product = Product.objects.get(Q(SKU=data.get('SKU')) | Q(URL=data.get('URL')))
            product.StockAvailability = stock_availability
            product.save()

            serializer = self.get_serializer(product)

            return Response(data={
                'success': True,
                'message': 'StockAvailability Updated!',
                'data': serializer.data,
            })

        except Product.DoesNotExist:
            return Response(data={
                'success': False,
                'message': 'Product Not Found!'
            }, status=status.HTTP_404_NOT_FOUND)

