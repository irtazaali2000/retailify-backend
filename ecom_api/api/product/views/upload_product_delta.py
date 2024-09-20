import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from api.product.serializers import *
from api.product.models import *

LOGGER = logging.getLogger(__name__)


class ProductUpload(CreateAPIView):
    serializer_class = ProductSerializer

    def is_update(self, instance, data):
        if 'StockAvailability' in data and data['StockAvailability'] != instance.StockAvailability:
            LOGGER.info(f"Product availabilty Updated {instance.StockAvailability} to {data['StockAvailability']}!")
            return True
        elif 'Offer' in data and data['Offer'] is not None and instance.Offer is not None and float(data['Offer']) != float(instance.Offer):
            LOGGER.info(f"Product Offer Updated from {instance.Offer} to {data['Offer']}!")
            return True
        elif 'RegularPrice' in data and float(data['RegularPrice']) != float(instance.RegularPrice):
            LOGGER.info(f"Product RegularPrice Updated from {instance.RegularPrice} to {data['RegularPrice']}!")
            return True
        elif 'RatingValue' in data and float(data['RatingValue']) != float(instance.RatingValue):
            LOGGER.info(f"Product RatingValue Updated from {instance.RatingValue} to {data['RatingValue']}!")
            return True

        else:
            return False

    def update_related_categories(self, instance):
        # Update related category data if CatalogueCode is updated
        if instance.CatalogueCode_id:
            categories = Category.objects.filter(CategoryCode=instance.CategoryCode_id)
            for category in categories:
                if category.CategoryName != instance.CategoryName:  # Check if there's a change in category name
                    old_category_name = category.CategoryName
                    category.CategoryName = instance.CategoryName
                    category.save()
                    LOGGER.info(f"Category Updated: {category.CategoryCode}. Name updated from '{old_category_name}' to '{category.CategoryName}'")
                else:
                    pass
                    #LOGGER.info(f"Category: No change in category name. Name: '{category.CategoryName}'")

            # # Check if the category doesn't exist and add it
            # if not categories.exists():
            #     new_category = Category.objects.create(
            #         CategoryCode=instance.CategoryCode_id,
            #         CategoryName=instance.CategoryName
            #     )
            #     LOGGER.info(f"New Category Added: {new_category.CategoryCode}. Name: '{new_category.CategoryName}'")






    def update_category_name_mapping(self, instance):
        # Update related category name mapping data if CategoryCode is updated
        if instance.CategoryCode_id:
            mapping = CategoryNameMapping.objects.filter(
                VendorCode=instance.VendorCode_id,
                CategoryCode=instance.CategoryCode_id
            ).first()

            if mapping:
                old_category_name = mapping.CategoryName
                if mapping.CategoryName != instance.CategoryName:  # Check if there's a change in category name
                    mapping.CategoryName = instance.CategoryName
                    mapping.save()
                    LOGGER.info(f"CategoryNameMapping Updated: {mapping.id}. Name updated from '{old_category_name}' to '{mapping.CategoryName}'")
                else:
                    pass
                    #LOGGER.info(f"CategoryNameMapping: No change in category name. Name: '{mapping.CategoryName}'")
            else:
                mapping = CategoryNameMapping.objects.create(
                    VendorCode=instance.VendorCode,
                    CategoryCode=instance.CategoryCode,
                    CategoryName=instance.CategoryName
                )
                LOGGER.info(f"CategoryNameMapping Created: {mapping.id}. Name: '{mapping.CategoryName}'")



    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        image = data.pop('MainImage')
        additional_properties = data.pop('AdditionalProperty', [])
        reviews = data.pop('reviews', [])

        try:
            instance = Product.objects.get(Q(SKU=data.get('SKU')) | Q(URL=data.get('URL')))
            if self.is_update(instance, data):
                if not data.get('StockAvailability'):
                    data['RegularPrice'] = instance.RegularPrice
                    data['Offer'] = instance.Offer
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    LOGGER.info(f"Product Updated: {instance.SKU}")
                    # Update related category data and CategoryNameMapping
                    self.update_related_categories(instance)
                    self.update_category_name_mapping(instance)
        
        except Product.DoesNotExist:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                LOGGER.info(f"Product Inserted: {instance.SKU}")
                # Update related category data and CategoryNameMapping
                self.update_related_categories(instance)
                self.update_category_name_mapping(instance)
                # if 'MainImage' in image:
                if image:
                    img_serializer = ImageSerializer(data={
                        'ProductCode': instance.ProductCode,
                        'SKU': instance.SKU,
                        'image_url': image
                        
                    })
                    if img_serializer.is_valid(raise_exception=True):
                        img_serializer.save()
                        LOGGER.info(f"Product Images Inserted: {instance.SKU}")

                        # Update the MainImage field in the Product instance after saving the image
                        instance.MainImage = image  # This updates the MainImage field in the Product table
                        instance.save(update_fields=['MainImage'])  # Save only the MainImage field
                    
                    else:
                        LOGGER.error(f"Image Serializer Errors: {img_serializer.errors}")
                        #return Response(data={'error': True, 'message': 'Image upload failed', 'details': img_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                if additional_properties:
                    ap_serializer = AdditionalPropertiesSerializer(data={
                        'ProductCode': instance.ProductCode,
                        'SKU': instance.SKU,
                        'AdditionalProperty': json.dumps(additional_properties)
                    })
                    if ap_serializer.is_valid(raise_exception=True):
                        ap_serializer.save()
                    LOGGER.info(f"Product AdditionalProperty Inserted: {instance.SKU}")

        
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
                
        #Means The Scraped Data is same as the Data in the Database so nothing happens
        return Response(data={'error': False, 'message': 'Product added'})
