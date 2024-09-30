import json
import logging
from django.db.models import Q

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from api.product.serializers import *
from api.product.models import *


class ProductUpload(CreateAPIView):
    serializer_class = ProductSerializer

    def is_update(self, instance, data):
        # if 'StockAvailability' in data and data['StockAvailability'] != instance.StockAvailability:
        #     print(f"Product availabilty Updated {instance.StockAvailability} to {data['StockAvailability']}!")
        #     return True
        # if 'Offer' in data and data['Offer'] is not None and instance.Offer is not None and float(data['Offer']) != float(instance.Offer):
        #     print(f"Product Offer Updated from {instance.Offer} to {data['Offer']}!")
        #     return True
        # if 'RegularPrice' in data and float(data['RegularPrice']) != float(instance.RegularPrice):
        #     print(f"Product RegularPrice Updated from {instance.RegularPrice} to {data['RegularPrice']}!")
        #     return True
        # if 'RatingValue' in data and float(data['RatingValue']) != float(instance.RatingValue):
        #     print(f"Product RatingValue Updated from {instance.RatingValue} to {data['RatingValue']}!")
        #     return True
        return False

    def update_related_categories(self, instance):
        if instance.CatalogueCode_id:
            categories = Category.objects.filter(CategoryCode=instance.CategoryCode_id)
            for category in categories:
                if category.CategoryName != instance.CategoryName:
                    old_category_name = category.CategoryName
                    category.CategoryName = instance.CategoryName
                    category.save()
                    print(f"Category Updated: {category.CategoryCode}. Name updated from '{old_category_name}' to '{category.CategoryName}'")

    def update_category_name_mapping(self, instance):
        if instance.CategoryCode_id:
            mapping = CategoryNameMapping.objects.filter(
                VendorCode=instance.VendorCode_id,
                CategoryCode=instance.CategoryCode_id
            ).first()

            if mapping:
                old_category_name = mapping.CategoryName
                if mapping.CategoryName != instance.CategoryName:
                    mapping.CategoryName = instance.CategoryName
                    mapping.save()
                    print(f"CategoryNameMapping Updated: {mapping.id}. Name updated from '{old_category_name}' to '{mapping.CategoryName}'")
            else:
                mapping = CategoryNameMapping.objects.create(
                    VendorCode=instance.VendorCode,
                    CategoryCode=instance.CategoryCode,
                    CategoryName=instance.CategoryName
                )
                print(f"CategoryNameMapping Created: {mapping.id}. Name: '{mapping.CategoryName}'")

    def create_dynamic_attributes(self, instance, attributes):
        """
        Create or update dynamic product attributes in ProductAttribute or OurStoreProductAttribute model.
        """
        for attribute in attributes:
            OurStoreProductAttribute.objects.update_or_create(
                ProductCode=instance,
                AttributeName=attribute.get('name'),
                defaults={'AttributeValue': attribute.get('value')}
            )
            print(f"Product Attribute Inserted/Updated: {attribute.get('name')} = {attribute.get('value')}")

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        image = data.pop('MainImage', None)
        additional_properties = data.pop('AdditionalProperty', [])
        reviews = data.pop('reviews', [])
        dynamic_attributes = data.pop('attributes', [])  # This will contain category-specific attributes

        try:
            instance = OurStoreProduct.objects.get(Q(SKU=data.get('SKU')) | Q(URL=data.get('URL')))
            if self.is_update(instance, data):
                if not data.get('StockAvailability'):
                    data['RegularPrice'] = instance.RegularPrice
                    data['Offer'] = instance.Offer
                serializer = self.serializer_class(instance=instance, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    print(f"Product Updated: {instance.SKU}")
                    self.update_related_categories(instance)
                    self.update_category_name_mapping(instance)
                    self.create_dynamic_attributes(instance, dynamic_attributes)  # Handle dynamic attributes
        
        except OurStoreProduct.DoesNotExist:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                print(f"Product Inserted: {instance.SKU}")
                # self.update_related_categories(instance)
                # self.update_category_name_mapping(instance)
                self.create_dynamic_attributes(instance, dynamic_attributes)  # Handle dynamic attributes
                
                if image:
                    img_serializer = ImageSerializer(data={
                        'ProductCode': instance.ProductCode,
                        'SKU': instance.SKU,
                        'image_url': image
                    })
                    if img_serializer.is_valid(raise_exception=True):
                        img_serializer.save()
                        print(f"Product Images Inserted: {instance.SKU}")
                        instance.MainImage = image
                        instance.save(update_fields=['MainImage'])

                if additional_properties:
                    ap_serializer = AdditionalPropertiesSerializer(data={
                        'ProductCode': instance.ProductCode,
                        'SKU': instance.SKU,
                        'AdditionalProperty': json.dumps(additional_properties)
                    })
                    if ap_serializer.is_valid(raise_exception=True):
                        ap_serializer.save()
                    print(f"Product AdditionalProperty Inserted: {instance.SKU}")

                if reviews:
                    for review_data in reviews:
                        if 'Comment' in review_data and review_data['Comment']:
                            existing_reviews = Review.objects.filter(
                                Comment=review_data['Comment'], 
                                CommentDate=review_data['CommentDate'],
                                Source=review_data['Source']
                            )
                            if existing_reviews.exists():
                                pass
                            else:
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
                                    print(f"Product Review Inserted: {instance.SKU}")
                                else:
                                    print(f"Review Serializer Errors: {review_serializer.errors}")

        return Response(data={'error': False, 'message': 'Product added'})
