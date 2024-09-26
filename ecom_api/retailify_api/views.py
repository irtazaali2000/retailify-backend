from rest_framework import generics
from rest_framework.views import APIView
from api.product.models import *
from .serializers import (VendorSerializer, CatalogueSerializer, CategorySerializer, 
                          ProductSerializer, ReviewSerializer, ImageSerializer, CustomProductSerializer,
                          OurStoreProduct, ProductDetailsByCategorySerializer,
                          )

from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, Value, DecimalField, F ,Q, Func, IntegerField
from decimal import Decimal
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.exceptions import ValidationError
from django.db.models.functions import Coalesce, Lower, Round
from concurrent.futures import ThreadPoolExecutor
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Sum, Case, When
from calendar import month_name
from django.utils import timezone
from django.db.models.functions import TruncMonth

from concurrent.futures import ThreadPoolExecutor, as_completed
from django.db.models import Prefetch
from django.core.cache import cache
from urllib.parse import quote
import hashlib
import time
from math import ceil
from django.db import connection

# Vendor API Views
class VendorList(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class VendorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

# Catalogue API Views
class CatalogueList(generics.ListCreateAPIView):
    queryset = Catalogue.objects.all()
    serializer_class = CatalogueSerializer

class CatalogueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Catalogue.objects.all()
    serializer_class = CatalogueSerializer

# Category API Views
class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Product API Views
class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Review API Views
class ReviewList(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

# Image API Views
class ImageList(generics.ListCreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer



############### CUSTOM ENDPOINT #################

class CustomProductList(generics.ListCreateAPIView):
    queryset = OurStoreProduct.objects.all()
    serializer_class = CustomProductSerializer

    def get_queryset(self):
        return super().get_queryset()
    


class ProductsWithMultipleVendorsByCategoryView(generics.ListAPIView):
    serializer_class = VendorSerializer

    def get_queryset(self):
        # Define the global price range (0 to 99999999)
        min_price = Decimal('0')
        max_price = Decimal('99999999')

        # Find products grouped by category and with similar price ranges
        queryset = Product.objects.filter(
            RegularPrice__gte=min_price,
            RegularPrice__lte=max_price
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({"detail": "No products found."}, status=status.HTTP_404_NOT_FOUND)

        vendors = {}

        # Set a threshold for considering prices "similar" (e.g., within 5% difference)
        price_similarity_threshold = Decimal('0.05')

        for product in queryset:
            if product.RegularPrice:
                # Find products in the same category with a similar price range
                lower_bound = product.RegularPrice * (Decimal('1') - price_similarity_threshold)
                upper_bound = product.RegularPrice * (Decimal('1') + price_similarity_threshold)

                # Look for products in the same category but with different vendors
                similar_products = Product.objects.filter(
                    RegularPrice__gte=lower_bound,
                    RegularPrice__lte=upper_bound,
                    CategoryCode=product.CategoryCode
                ).exclude(ProductCode=product.ProductCode)

                if similar_products.exists():
                    category_name = product.CategoryCode.CategoryName
                    if category_name not in vendors:
                        vendors[category_name] = []

                    # Add the similar products to the vendor list
                    for similar_product in similar_products:
                        serializer = VendorSerializer(similar_product)
                        vendors[category_name].append(serializer.data)

        if not vendors:
            return Response({"detail": "No similar products found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"retailers": vendors}, status=status.HTTP_200_OK)


    


class CompareProductsView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        try:
            # Get user input parameters (optional)
            brand_name = request.GET.get('brand_name', None)
            category_name = request.GET.get('category_name', None)
            product_name = request.GET.get('product_name', None)
            min_price = request.GET.get('min_price', None)
            max_price = request.GET.get('max_price', None)

            # Get pagination parameters
            page_size = int(request.GET.get('page_size', 5))  # Default to 5 products per page
            page = int(request.GET.get('page', 1))  # Default to page 1

            # Base SQL query for ModelNumber matching
            query = '''
                SELECT 
                    p."ProductCode" AS product_product_code,
                    p."ProductName" AS product_product_name,
                    p."SKU" AS product_sku,
                    p."ModelNumber" AS product_model_number,
                    p."BrandName" AS product_brand_name,
                    p."RegularPrice" AS product_regular_price,
                    p."Offer" AS product_offer_price,
                    p."Currency" AS product_currency,
                    p."StockAvailability" AS product_stock,  -- Fetch stock availability
                    v."VendorName" AS vendor_name,  -- Fetch VendorName from Vendor model
                    os."ProductCode" AS ourstore_product_code,
                    os."ProductName" AS ourstore_product_name,
                    os."SKU" AS ourstore_sku,
                    os."ModelNumber" AS ourstore_model_number,
                    os."BrandName" AS ourstore_brand_name,
                    os."MyPrice" AS ourstore_my_price,
                    os."Currency" AS ourstore_currency,
                    os."MainImage" AS ourstore_image,
                    os."Cost" AS ourstore_cost,
                    os."About" AS ourstore_about

                FROM 
                    product_product p
                JOIN 
                    product_ourstoreproduct os
                ON 
                    (p."ModelNumber" = os."ModelNumber"
                    OR p."ModelNumber" LIKE TRIM(BOTH FROM os."ModelNumber"))

                JOIN 
                    product_vendor v  -- Join Vendor table
                ON 
                    p."VendorCode_id" = v."VendorCode"  -- Use VendorCode_id for the foreign key
            '''

            # Dynamic filters
            query_conditions = []
            query_params = []

            if brand_name:
                query_conditions.append('LOWER(p."BrandName") = LOWER(%s) AND LOWER(os."BrandName") = LOWER(%s)')
                query_params.extend([brand_name, brand_name])

            if category_name:
                query_conditions.append('p."CategoryName" ILIKE %s')
                query_params.append(f'%{category_name}%')

            if product_name:
                query_conditions.append('os."ProductName" ILIKE %s')
                query_params.append(f'%{product_name}%')
            
            if min_price:
                query_conditions.append('os."MyPrice" >= %s')
                query_params.append(min_price)

            if max_price:
                query_conditions.append('os."MyPrice" <= %s')
                query_params.append(max_price)

            if query_conditions:
                query += " AND " + " AND ".join(query_conditions)

            with connection.cursor() as cursor:
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                model_number_result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                print(f"SQL Query Result Count: {len(model_number_result)}")

            # Prepare results for model number matches
            product_map = {}
            for product in model_number_result:
                sku = product['ourstore_sku']
                if sku not in product_map:
                    product_map[sku] = {
                        "ProductName": product['ourstore_product_name'],
                        "SKU": product['ourstore_sku'],
                        "MyPrice": product['ourstore_my_price'],
                        "ModelNumber": product['ourstore_model_number'],
                        "Currency": product['ourstore_currency'],
                        "MainImage": product['ourstore_image'],
                        "Cost": product['ourstore_cost'],
                        "Brand": product['ourstore_brand_name'],
                        "About": [product['ourstore_about']],
                        "match_by": "ModelNumber",
                        "Vendors": [],
                    }

                # Functions for calculating additional keys
                def get_stock(obj):
                    return "Instock" if obj['product_stock'] else "Out of stock"

                def get_discounted_price(obj):
                    return obj['product_offer_price'] if obj['product_offer_price'] else 0

                def get_regular_price(obj):
                    return obj['product_regular_price']

                def get_price_match(our_product, obj):
                    retailer_price = obj['product_offer_price'] if obj['product_offer_price'] else obj['product_regular_price']
                    if our_product and retailer_price:
                        price_difference = our_product['MyPrice'] - retailer_price
                        price_match_percentage = (price_difference / our_product['MyPrice']) * 100 if our_product['MyPrice'] != 0 else 0
                        return round(price_match_percentage, 2)
                    return 0

                def get_net_match(our_product, obj):
                    retailer_price = obj['product_offer_price'] if obj['product_offer_price'] else obj['product_regular_price']
                    if our_product and retailer_price and our_product['Cost']:
                        net_margin = (retailer_price - our_product['Cost']) / our_product['Cost'] * 100
                        return round(net_margin, 2)
                    return 0

                def get_discount(obj):
                    if obj['product_offer_price'] and obj['product_regular_price'] and obj['product_regular_price'] != 0:
                        discount_percentage = round(((obj['product_regular_price'] - obj['product_offer_price']) / obj['product_regular_price']) * 100, 2)
                        return discount_percentage
                    return 0

                # Append vendor details with new keys
                product_map[sku]["Vendors"].append({
                    "VendorName": product['vendor_name'],
                    "SKU": product['product_sku'],
                    "ModelNumber": product['product_model_number'],
                    "Price": product['product_offer_price'] or product['product_regular_price'],
                    "Currency": product['product_currency'],
                    "ProductName": product['product_product_name'],
                    "Stock": get_stock(product),
                    "DiscountedPrice": get_discounted_price(product),
                    "RegularPrice": get_regular_price(product),
                    "PriceMatch": get_price_match(product_map[sku], product),
                    "NetMatch": get_net_match(product_map[sku], product),
                    "Discount": get_discount(product),
                })

            # Filter out products with empty "Vendors"
            total_matches_before_filter = len(product_map)  # Include all products in the count
            print(f"Total Matches Before Filter: {total_matches_before_filter}")
            filtered_results = [product for product in product_map.values() if product["Vendors"]]

            # Convert dict to list for response
            final_result = filtered_results

            # Apply pagination
            paginator = Paginator(final_result, page_size)
            page_data = paginator.page(page)

            # Prepare the response
            response_data = {
                'products': page_data.object_list,
                'page': page,
                'page_size': page_size,
                'next_page': page_data.has_next(),
                'previous_page': page_data.has_previous(),
                'total_matches': len(final_result)
            }

            return Response(response_data)

        except EmptyPage:
            return Response({'message': 'Page not found'}, status=404)

        except Exception as e:
            return Response({'message': str(e)}, status=404)





class CompareProductsByNameView(generics.GenericAPIView):
    """
    Compare products between the Product and OurStoreProduct tables based on user input for product name with pagination.
    """
    serializer_class = VendorSerializer
    
    def process_product(self, our_product, lower_product_name):
        # Approximate matching using TrigramSimilarity on the product name
        matching_products = Product.objects.annotate(
            similarity=TrigramSimilarity(F('ProductName'), lower_product_name)
        ).annotate(
            similarity_rounded=Round(F('similarity'), 2)  # Round similarity score for better accuracy
        ).filter(
            Q(similarity_rounded__gt=0.2)  # Strict threshold for similarity score
        ).order_by('-similarity_rounded')

        if matching_products.exists():
            vendor_products = []
            for product in matching_products:
                serializer = VendorSerializer(product, context={'our_product': our_product})
                serialized_data = serializer.data
                serialized_data['similarity_score'] = product.similarity_rounded
                vendor_products.append(serialized_data)

            comparison = {
                "our_store_product": {
                    "name": our_product.ProductName,
                    "sku": our_product.SKU,
                    "brand": our_product.BrandName,
                    "my_price": our_product.MyPrice,
                    "cost": our_product.Cost,
                    "currency": our_product.Currency,
                    "image_url": our_product.MainImage if our_product.MainImage else '',  # Adjust if MainImage is an ImageField
                    'about': [our_product.About],
                },
                "retailer_products": vendor_products
            }
            return comparison
        return None


    def get(self, request, *args, **kwargs):
        # Get the product name from user input (query parameter)
        product_name = request.query_params.get('product_name', None)
        
        if not product_name:
            raise ValidationError("Please provide a 'product_name' query parameter.")

        # Convert product name to lowercase for case-insensitive matching
        lower_product_name = product_name.lower()

        # Fetch products from OurStoreProduct that approximately match the input product name
        our_store_products = OurStoreProduct.objects.annotate(
            similarity=TrigramSimilarity(F('ProductName'), lower_product_name)
        ).annotate(
            similarity_rounded=Round(F('similarity'), 2)  # Round similarity score for better accuracy
        ).filter(
            Q(ProductName__icontains=lower_product_name) |  # Prioritize exact matches
            Q(similarity_rounded__gt=0.2)  # Increase similarity threshold to reduce irrelevant matches
        ).order_by('-similarity_rounded')

        # Apply price filtering if min_price or max_price is provided
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)

        if min_price is not None:
            our_store_products = our_store_products.filter(MyPrice__gte=min_price)
        if max_price is not None:
            our_store_products = our_store_products.filter(MyPrice__lte=max_price)

        # Paginate results
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)  # Default to 10 items per page
        paginator = Paginator(our_store_products, page_size)

        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        compared_products = []
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda p: self.process_product(p, lower_product_name), page.object_list))

        # Filter out any None results (if no matching products were found for certain our_store_products)
        compared_products = [result for result in results if result is not None]

        return Response({
            'results': compared_products,
            'page': page.number,
            'page_size': page.paginator.per_page,
            'total_pages': page.paginator.num_pages,
            'total_count': page.paginator.count
        })




class CompareProductsByCategoryView(generics.GenericAPIView):
    """
    Compare products between the Product and OurStoreProduct tables based on user input for category name with pagination.
    """
    serializer_class = VendorSerializer
    
    def process_product(self, our_product):
        # Prefetch related VendorCode for better performance and do exact category matching
        matching_products = Product.objects.select_related('VendorCode').filter(
            CategoryName__iexact=our_product.CategoryName  # Case-insensitive exact match for CategoryName
        )
        # .annotate(similarity=TrigramSimilarity('ProductName', our_product.ProductName)  # Match based on product name
        # .filter(similarity__gt=0.1).order_by('-similarity')  # Use a higher threshold for similarity score

        if matching_products.exists():
            vendor_products = []
            for product in matching_products:
                serializer = VendorSerializer(product, context={'our_product': our_product})
                serialized_data = serializer.data
               # serialized_data['similarity_score'] = product.similarity
                vendor_products.append(serialized_data)

            comparison = {
                "our_store_product": {
                    "name": our_product.ProductName,
                    'category': our_product.CategoryName,
                    "sku": our_product.SKU,
                    "brand": our_product.BrandName,
                    "my_price": our_product.MyPrice,
                    "cost": our_product.Cost,
                    "currency": our_product.Currency,
                    "image_url": our_product.MainImage if our_product.MainImage else '',  # Adjust if MainImage is an ImageField
                    'about': [our_product.About]
                },
                "retailer_products": vendor_products
            }
            return comparison
        return None

    def get(self, request, *args, **kwargs):
        # Get the category name from user input (query parameter)
        input_category_name = request.query_params.get('category_name', None)
        
        if not input_category_name:
            raise ValidationError("Please provide a 'category_name' query parameter.")

        # Get pagination parameters
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)

        # Fetch products from OurStoreProduct that approximately match the input category name
        our_store_products = OurStoreProduct.objects.filter(
            CategoryName__icontains=input_category_name  # Use icontains for broader matching
        )

        # Apply price filtering if min_price or max_price is provided
        if min_price is not None:
            our_store_products = our_store_products.filter(MyPrice__gte=min_price)
        if max_price is not None:
            our_store_products = our_store_products.filter(MyPrice__lte=max_price)

        # Sort by relevance based on the matching category name
        our_store_products = our_store_products.order_by('CategoryName')

        if not our_store_products.exists():
            return Response({"message": "No products found in OurStoreProduct for the given name and range."})

        # Paginate results
        paginator = Paginator(our_store_products, page_size)
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page = paginator.page(paginator.num_pages)

        compared_products = []
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(self.process_product, page.object_list))

        # Filter out any None results (if no matching products were found for certain our_store_products)
        compared_products = [result for result in results if result is not None]

        return Response({
            'results': compared_products,
            'page': page.number,
            'page_size': page.paginator.per_page,
            'total_pages': page.paginator.num_pages,
            'total_count': page.paginator.count
        })

    

class CompareProductsByBrandView(generics.GenericAPIView):
    """
    Compare products between the Product and OurStoreProduct tables based on user input for brand name with pagination.
    """
    serializer_class = VendorSerializer

    def process_product(self, our_product, lower_brand_name):
        # Approximate matching using TrigramSimilarity on the brand name
        matching_products = Product.objects.annotate(
            similarity=TrigramSimilarity(F('BrandName'), lower_brand_name)
        ).annotate(
            similarity_rounded=Round(F('similarity'), 2)  # Round similarity score for better accuracy
        ).filter(
            Q(BrandName__icontains=lower_brand_name) |  # Prioritize exact matches
            Q(similarity_rounded__gt=0.29)  # Increase similarity threshold to reduce irrelevant matches
        ).order_by('-similarity_rounded')

        if matching_products.exists():
            vendor_products = []
            for product in matching_products:
                serializer = VendorSerializer(product, context={'our_product': our_product})
                serialized_data = serializer.data
                serialized_data['similarity_score'] = product.similarity_rounded
                vendor_products.append(serialized_data)

            comparison = {
                "our_store_product": {
                    "name": our_product.ProductName,
                    'category': our_product.CategoryName,
                    "sku": our_product.SKU,
                    "brand": our_product.BrandName,
                    "my_price": our_product.MyPrice,
                    "cost": our_product.Cost,
                    "currency": our_product.Currency,
                    "image_url": our_product.MainImage if our_product.MainImage else '',  # Adjust if MainImage is an ImageField
                    'about': [our_product.About]
                },
                "retailer_products": vendor_products
            }
            return comparison
        return None

    def get(self, request, *args, **kwargs):
        # Get the brand name from user input (query parameter)
        input_brand_name = request.query_params.get('brand_name', None)

        if not input_brand_name:
            raise ValidationError("Please provide a 'brand_name' query parameter.")

        # Convert brand name to lowercase for case-insensitive matching
        lower_brand_name = input_brand_name.lower()

        # Fetch products from OurStoreProduct that approximately match the input brand name
        our_store_products = OurStoreProduct.objects.annotate(
            similarity=TrigramSimilarity(F('BrandName'), lower_brand_name)
        ).annotate(
            similarity_rounded=Round(F('similarity'), 2)  # Round similarity score for better accuracy
        ).filter(
            Q(BrandName__icontains=lower_brand_name) |  # Prioritize exact matches
            Q(similarity_rounded__gt=0.2)  # Increase similarity threshold to reduce irrelevant matches
        ).order_by('-similarity_rounded')

        # Apply price filtering if min_price or max_price is provided
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)

        if min_price is not None:
            our_store_products = our_store_products.filter(MyPrice__gte=min_price)
        if max_price is not None:
            our_store_products = our_store_products.filter(MyPrice__lte=max_price)

        # Paginate results
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)  # Default to 10 items per page
        paginator = Paginator(our_store_products, page_size)

        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        compared_products = []
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda p: self.process_product(p, lower_brand_name), page.object_list))

        # Filter out any None results (if no matching products were found for certain our_store_products)
        compared_products = [result for result in results if result is not None]

        return Response({
            'results': compared_products,
            'page': page.number,
            'page_size': page.paginator.per_page,
            'total_pages': page.paginator.num_pages,
            'total_count': page.paginator.count
        })

    

class AllVendorNames(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        vendors = Vendor.objects.values_list('VendorName', flat=True)
        return Response(list(vendors))
    
class AllBrandNames(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        brands = OurStoreProduct.objects.values_list('BrandName', flat=True).distinct()
        return Response(list(brands))

class AllCategoryNames(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.values_list('CategoryName', flat=True)
        return Response(list(categories))
    
class AllCatalogueNames(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        categories = Catalogue.objects.values_list('CatalogueName', flat=True)
        return Response(list(categories))


class ProductDetailsByCategoryView(generics.GenericAPIView):
    serializer_class = ProductDetailsByCategorySerializer

    def get(self, request, *args, **kwargs):
        # Perform aggregation: total price and total products per category
        categories = Category.objects.annotate(
            total_price=Coalesce(Sum('ourstoreproduct__MyPrice'), Value(0), output_field=DecimalField()),  # Sum of RegularPrice in Product
            total_products=Count('ourstoreproduct')  # Count of products in each category
        ).values(
            'total_price', 
            'total_products',
             category_name=F('CategoryName'),  # Use alias to rename the key
        )

        # Serialize the data
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class CountBrandProductCategoryView(generics.GenericAPIView):
    #serializer = CountBrandProductCategorySerializer

    def get(self, request, *args, **kwargs):
        category_count = Category.objects.exclude(CategoryName='').values('CategoryName').distinct().count()
        brand_count = OurStoreProduct.objects.exclude(BrandName='').values('BrandName').distinct().count()
        product_count = OurStoreProduct.objects.all().count()

        data = {
            'brand_count': brand_count,
            'category_count': category_count,
            'product_count': product_count
        }

        return Response(data)

    
class CountStockAvailabilityView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        # OurStoreProduct Stock Data
        ourstore_instock = OurStoreProduct.objects.filter(StockAvailability=True).count()
        ourstore_outstock = OurStoreProduct.objects.filter(StockAvailability=False).count()
        ourstore_total_products = ourstore_instock + ourstore_outstock
        
        # Calculate in-stock percentage for OurStoreProduct
        if ourstore_total_products > 0:
            ourstore_instock_percentage = round(float(ourstore_instock / ourstore_total_products * 100), 2)
        else:
            ourstore_instock_percentage = 0

        # Calculate the total stock value of in-stock OurStoreProduct items
        ourstore_stock_value = OurStoreProduct.objects.filter(StockAvailability=True).aggregate(total_value=Sum(F('MyPrice')))['total_value'] or 0

        # Vendors (Product Model) Stock Data
        vendors_instock = Product.objects.filter(StockAvailability=True).count()
        vendors_outstock = Product.objects.filter(StockAvailability=False).count()
        vendors_total_products = vendors_instock + vendors_outstock

        # Calculate in-stock percentage for vendors
        if vendors_total_products > 0:
            vendors_instock_percentage = round(float(vendors_instock / vendors_total_products * 100), 2)
        else:
            vendors_instock_percentage = 0

        # Calculate total stock value for each vendor (Product model) and find the vendor with the highest stock value
        vendor_stock_values = Product.objects.filter(StockAvailability=True).values('VendorCode__VendorName').annotate(
            total_value=Sum(F('Offer'))
        ).order_by('-total_value')

        highest_stock_vendor = vendor_stock_values.first() if vendor_stock_values.exists() else None

        data = {
            'ourstore_instock': ourstore_instock,
            'ourstore_outstock': ourstore_outstock,
            'ourstore_instock_percentage': ourstore_instock_percentage,
            'ourstore_stock_value': round(ourstore_stock_value, 2),  # Total stock value of in-stock OurStoreProduct items

            'vendors_instock': vendors_instock,
            'vendors_outstock': vendors_outstock,
            'vendors_instock_percentage': vendors_instock_percentage,

            'highest_stock_vendor': {
                'vendor_name': highest_stock_vendor['VendorCode__VendorName'] if highest_stock_vendor else None,
                'vendor_stock_value': round(highest_stock_vendor['total_value'], 2) if highest_stock_vendor else 0
            }  # Vendor with the highest stock value
        }

        return Response(data)
    


class VendorDetailsByCategoryView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        # Get all categories and annotate them with the number of products
        categories = (
            Category.objects.annotate(product_count=Count('product'))
            .order_by('-product_count')
        )

        # Pagination using django.core.paginator
        page_number = request.GET.get('page', 1)
        paginator = Paginator(categories, 5)  # Show 5 categories per page

        try:
            paginated_categories = paginator.page(page_number)
        except PageNotAnInteger:
            paginated_categories = paginator.page(1)
        except EmptyPage:
            return Response({'message': 'Page not found'}, status=404)
            #paginated_categories = paginator.page(paginator.num_pages)

        # Prepare the response data for each category
        results = []
        for category in paginated_categories:
            # Get all products within the current category
            products = Product.objects.filter(CategoryCode=category)
            # Get the count of products in OurStoreProduct for the same category
            store_products_count = OurStoreProduct.objects.filter(CategoryCode=category).count()

            # Aggregate stock level, stock availability, and stock value (price) per vendor for the current category
            vendors_data = products.values('VendorCode__VendorName').annotate(
                stock_level=Count('ProductCode'),  # Stock level is the count of products
                stock_availability=Sum(Case(When(StockAvailability=True, then=1), default=0)),
                total_stock=Count('ProductCode'),
                stock_value=Sum(
                    Case(
                        When(Offer__gt=0, then=F('Offer')),  # Use Offer price if it's greater than 0
                        default=F('RegularPrice')  # Otherwise, use RegularPrice
                    )
                )
            )

            # Structure vendor data for each category
            vendor_details = {}
            for vendor in vendors_data:
                vendor_name = vendor['VendorCode__VendorName']
                stock_availability_percentage = (vendor['stock_availability'] / vendor['total_stock']) * 100
                stock_status = 'Instock' if stock_availability_percentage > 40 else 'Out of Stock'

                vendor_details[vendor_name] = {
                    'stock_availability': round(float(stock_availability_percentage), 2),
                    'stock_level': vendor['stock_level'],  # Renamed from stock_value to stock_level
                    'stock_value': vendor['stock_value'],  # Total price of all products
                    'stockStatus': stock_status
                }

            # Add category details to the results list
            results.append({
                'qty': store_products_count,
                'name': category.CategoryName,
                'vendors': vendor_details
            })

        # Return paginated response in the desired format
        return Response({
            'results': results,
            'page': paginated_categories.number,
            'page_size': paginator.per_page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count
        })
    


class VendorDetailsByBrandView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        # Get all brands and annotate them with the number of products from the OurStoreProduct model
        brands = (
            OurStoreProduct.objects.values('BrandName')
            .annotate(product_count=Count('ProductCode'))
            .order_by('-product_count')
        )

        # Pagination using django.core.paginator
        page_number = request.GET.get('page', 1)
        paginator = Paginator(brands, 5)  # Show 5 brands per page

        try:
            paginated_brands = paginator.page(page_number)
        except PageNotAnInteger:
            paginated_brands = paginator.page(1)
        except EmptyPage:
            return Response({'message': 'Page not found'}, status=404)
            #paginated_brands = paginator.page(paginator.num_pages)

        # Prepare the response data for each brand
        results = []
        for brand in paginated_brands:
            # Get all products within the current brand from the Product model
            products = Product.objects.filter(BrandName=brand['BrandName'])

            # Aggregate stock level, stock availability, and stock value (price) per vendor for the current brand
            vendors_data = products.values('VendorCode__VendorName').annotate(
                stock_level=Count('ProductCode'),  # Count of products
                stock_availability=Sum(Case(When(StockAvailability=True, then=1), default=0)),
                total_stock=Count('ProductCode'),
                stock_value=Sum(
                    Case(
                        When(Offer__gt=0, then=F('Offer')),  # Use Offer price if it's greater than 0
                        default=F('RegularPrice')  # Otherwise, use RegularPrice
                    )
                )
            )

            # Structure vendor data for each brand
            vendor_details = {}
            for vendor in vendors_data:
                vendor_name = vendor['VendorCode__VendorName']
                stock_availability_percentage = (vendor['stock_availability'] / vendor['total_stock']) * 100
                stock_status = 'Instock' if stock_availability_percentage > 40 else 'Out of Stock'

                vendor_details[vendor_name] = {
                    'stock_availability': round(float(stock_availability_percentage), 2),
                    'stock_level': vendor['stock_level'],  # Renamed from stock_value to stock_level
                    'stock_value': vendor['stock_value'],  # Total price of all products for this vendor
                    'stockStatus': stock_status,
                }

            # Add brand details to the results list
            results.append({
                'name': brand['BrandName'],  # Brand name from OurStoreProduct
                'qty': brand['product_count'],  # Product count from OurStoreProduct
                'vendors': vendor_details
            })

        # Return paginated response in the desired format
        return Response({
            'results': results,
            'page': paginated_brands.number,
            'page_size': paginator.per_page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count
        })




class VendorDetailsByCatalogueView(generics.GenericAPIView):
    
    def get(self, request, *args, **kwargs):
        # Get all catalogues
        catalogues = Catalogue.objects.all()

        result = {}

        for catalogue in catalogues:
            # Get all products for the current catalogue
            products = Product.objects.filter(CatalogueCode=catalogue, StockAvailability=True)

            # Aggregate stock level and stock value per vendor for the current catalogue
            vendors_data = products.values('VendorCode__VendorName').annotate(
                stock_level=Count('ProductCode'),  # Count of in-stock products
                stock_value=Sum(
                    Case(
                        When(Offer__gt=0, then=F('Offer')),  # Use Offer price if it's greater than 0
                        default=F('RegularPrice')  # Otherwise, use RegularPrice
                    )
                )
            )

            # Structure vendor data for each catalogue
            vendor_details = []
            for vendor in vendors_data:
                vendor_name = vendor['VendorCode__VendorName']
                vendor_details.append({
                    'vendor': vendor_name,
                    'stock_level': vendor['stock_level'],  # Total in-stock products for this vendor
                    'stock_value': str(vendor['stock_value']),  # Total price of all products for this vendor
                })

            # Add catalogue details to the result dictionary
            result[catalogue.CatalogueName] = vendor_details

        # Return the response in the desired format
        return Response(result)


class InStockProductsByMonthView(generics.GenericAPIView):
    
    def get(self, request, *args, **kwargs):
        # Get the current date and the date from 2 months ago
        now = timezone.now()
        two_months_ago = now - timezone.timedelta(days=60)

        # Fetch Product data for vendors, grouping by month and VendorCode
        product_data = (
            Product.objects.filter(DateInserted__gte=two_months_ago, StockAvailability=True)
            .annotate(month=TruncMonth('DateInserted'))
            .values('month', 'VendorCode__VendorName')
            .annotate(instock_count=Count('ProductCode'))
        )

        # Fetch OurStoreProduct data for in-stock products, grouping by month
        our_store_data = (
            OurStoreProduct.objects.filter(DateInserted__gte=two_months_ago, StockAvailability=True)
            .annotate(month=TruncMonth('DateInserted'))
            .values('month')
            .annotate(instock_count=Count('ProductCode'))
        )

        # Create a dictionary to store the results grouped by month
        results = {}

        # Process the Product data (vendor products)
        for entry in product_data:
            month = month_name[entry['month'].month] + " " + str(entry['month'].year)
            vendor_name = entry['VendorCode__VendorName']
            if month not in results:
                results[month] = {"month": month}
            results[month][vendor_name] = entry['instock_count']

        # Process the OurStoreProduct data (our store's products)
        for entry in our_store_data:
            month = month_name[entry['month'].month] + " " + str(entry['month'].year)
            if month not in results:
                results[month] = {"month": month}
            results[month]['Our Stock'] = entry['instock_count']

        # Convert the results dictionary to a list
        final_results = list(results.values())

        return Response(final_results)


class CategoryPriceByYearView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        # Get the current date and the date from 12 months ago
        now = timezone.now()
        twelve_months_ago = now - timezone.timedelta(days=365)

        # Fetch the data from OurStoreProduct, grouping by month and category
        products_data = (
            OurStoreProduct.objects.filter(DateInserted__gte=twelve_months_ago)
            .annotate(month=TruncMonth('DateInserted'))  # Group by month
            .values('month', 'CategoryCode__CategoryName')  # Group by category
            .annotate(total_price=Sum('MyPrice'))  # Sum of MyPrice for each category
        )

        # Initialize a dictionary to store the data grouped by month
        results = {}

        # Process the data
        for entry in products_data:
            month = month_name[entry['month'].month] + " " + str(entry['month'].year)  # Get month name and year
            category_name = entry['CategoryCode__CategoryName']
            if month not in results:
                results[month] = {"month": month}
            results[month][category_name] = entry['total_price'] or 0  # Add the total price for each category

        # Convert the dictionary to a list
        final_results = list(results.values())

        return Response(final_results)
    




class IntelligenceProductPriceLower(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        try:
            # Get user input parameters (optional)
            brand_name = request.GET.get('brand_name', None)
            category_name = request.GET.get('category_name', None)
            product_name = request.GET.get('product_name', None)

            # Get pagination parameters
            page_size = int(request.GET.get('page_size', 5))  # Default to 5 products per page
            page = int(request.GET.get('page', 1))  # Default to page 1

            # Base SQL query for ModelNumber matching
            query = '''
                SELECT 
                    p."ProductCode" AS product_product_code,
                    p."ProductName" AS product_product_name,
                    p."SKU" AS product_sku,
                    p."ModelNumber" AS product_model_number,
                    p."BrandName" AS product_brand_name,
                    p."RegularPrice" AS product_regular_price,
                    p."Offer" AS product_offer_price,
                    p."Currency" AS product_currency,
                    p."StockAvailability" AS product_stock,
                    v."VendorName" AS vendor_name,  -- Fetch VendorName from Vendor model
                    os."ProductCode" AS ourstore_product_code,
                    os."ProductName" AS ourstore_product_name,
                    os."SKU" AS ourstore_sku,
                    os."ModelNumber" AS ourstore_model_number,
                    os."BrandName" AS ourstore_brand_name,
                    os."MyPrice" AS ourstore_my_price,
                    os."Currency" AS ourstore_currency,
                    os."MainImage" AS ourstore_image,
                    os."Cost" AS ourstore_cost,
                    os."About" AS ourstore_about
                FROM 
                    product_product p
                JOIN 
                    product_ourstoreproduct os
                ON 
                    (p."ModelNumber" = os."ModelNumber"
                    OR p."ModelNumber" LIKE TRIM(BOTH FROM os."ModelNumber"))
                JOIN 
                    product_vendor v  -- Join Vendor table
                ON 
                    p."VendorCode_id" = v."VendorCode"  -- Use VendorCode_id for the foreign key
                WHERE 
                    os."MyPrice" < COALESCE(NULLIF(p."Offer", 0), p."RegularPrice")

            '''

            # Dynamic filters
            query_conditions = []
            query_params = []

            if brand_name:
                query_conditions.append('LOWER(p."BrandName") = LOWER(%s) AND LOWER(os."BrandName") = LOWER(%s)')
                query_params.extend([brand_name, brand_name])

            if category_name:
                query_conditions.append('p."CategoryName" ILIKE %s')
                query_params.append(f'%{category_name}%')

            if product_name:
                query_conditions.append('os."ProductName" ILIKE %s')
                query_params.append(f'%{product_name}%')

            if query_conditions:
                query += " AND " + " AND ".join(query_conditions)

            with connection.cursor() as cursor:
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                model_number_result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                print(f"SQL Query Result Count: {len(model_number_result)}")

            # Prepare results for model number matches
            product_map = {}
            for product in model_number_result:
                sku = product['ourstore_sku']
                if sku not in product_map:
                    product_map[sku] = {
                        "ProductName": product['ourstore_product_name'],
                        "SKU": product['ourstore_sku'],
                        "MyPrice": product['ourstore_my_price'],
                        "ModelNumber": product['ourstore_model_number'],
                        "Currency": product['ourstore_currency'],
                        "MainImage": product['ourstore_image'],
                        "Cost": product['ourstore_cost'],
                        "Brand": product['ourstore_brand_name'],
                        "About": [product['ourstore_about']],
                        "match_by": "ModelNumber",
                        "VendorsWithHigherPrice": [], 
                    }


                # Functions for calculating additional keys
                def get_stock(obj):
                    return "Instock" if obj['product_stock'] else "Out of stock"

                def get_discounted_price(obj):
                    return obj['product_offer_price'] if obj['product_offer_price'] else 0

                def get_regular_price(obj):
                    return obj['product_regular_price']

                def get_price_match(our_product, obj):
                    retailer_price = obj['product_offer_price'] if obj['product_offer_price'] else obj['product_regular_price']
                    if our_product and retailer_price:
                        price_difference = our_product['MyPrice'] - retailer_price
                        price_match_percentage = (price_difference / our_product['MyPrice']) * 100 if our_product['MyPrice'] != 0 else 0
                        return round(price_match_percentage, 2)
                    return 0

                def get_net_match(our_product, obj):
                    retailer_price = obj['product_offer_price'] if obj['product_offer_price'] else obj['product_regular_price']
                    if our_product and retailer_price and our_product['Cost']:
                        net_margin = (retailer_price - our_product['Cost']) / our_product['Cost'] * 100
                        return round(net_margin, 2)
                    return 0

                def get_discount(obj):
                    if obj['product_offer_price'] and obj['product_regular_price'] and obj['product_regular_price'] != 0:
                        discount_percentage = round(((obj['product_regular_price'] - obj['product_offer_price']) / obj['product_regular_price']) * 100, 2)
                        return discount_percentage
                    return 0
                

                if product['ourstore_my_price'] < (product['product_offer_price'] or product['product_regular_price']):
                    product_map[sku]["VendorsWithHigherPrice"].append({
                        "VendorName": product['vendor_name'],  # Fetch the correct VendorName
                        "SKU": product['product_sku'],
                        "ModelNumber": product['product_model_number'],
                        "Price": product['product_offer_price'] or product['product_regular_price'],  # Offer first, then RegularPrice
                        "Currency": product['product_currency'],
                        "ProductName": product['product_product_name'],
                        "Stock": get_stock(product),
                        "DiscountedPrice": get_discounted_price(product),
                        "RegularPrice": get_regular_price(product),
                        "PriceMatch": get_price_match(product_map[sku], product),
                        "NetMatch": get_net_match(product_map[sku], product),
                        "Discount": get_discount(product),
                    })


            # Filter out products with empty "VendorsWithHigherPrice"
            total_matches_before_filter = len(product_map)  # Include all products in the count
            print(f"Total Matches Before Filter: {total_matches_before_filter}")
            filtered_results = [product for product in product_map.values() if product["VendorsWithHigherPrice"]]

            # Convert dict to list for response
            final_result = filtered_results

            # Apply pagination
            paginator = Paginator(final_result, page_size)
            page_data = paginator.page(page)

            # Prepare the response
            response_data = {
                'products': page_data.object_list,
                'page': page,
                'page_size': page_size,
                'next_page': page_data.has_next(),
                'previous_page': page_data.has_previous(),
                'total_matches': len(final_result)
            }

            return Response(response_data)

        except EmptyPage:
            return Response({'message': 'Page not found'}, status=404)

        except Exception as e:
            return Response({'message': str(e)}, status=404)


class IntelligenceProductPriceHigher(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        try:
            # Get user input parameters (optional)
            brand_name = request.GET.get('brand_name', None)
            category_name = request.GET.get('category_name', None)
            product_name = request.GET.get('product_name', None)

            # Get pagination parameters
            page_size = int(request.GET.get('page_size', 5))  # Default to 5 products per page
            page = int(request.GET.get('page', 1))  # Default to page 1

            # Base SQL query for ModelNumber matching
            query = '''
                SELECT 
                    p."ProductCode" AS product_product_code,
                    p."ProductName" AS product_product_name,
                    p."SKU" AS product_sku,
                    p."ModelNumber" AS product_model_number,
                    p."BrandName" AS product_brand_name,
                    p."RegularPrice" AS product_regular_price,
                    p."Offer" AS product_offer_price,
                    p."Currency" AS product_currency,
                    p."StockAvailability" AS product_stock,
                    v."VendorName" AS vendor_name,  -- Fetch VendorName from Vendor model
                    os."ProductCode" AS ourstore_product_code,
                    os."ProductName" AS ourstore_product_name,
                    os."SKU" AS ourstore_sku,
                    os."ModelNumber" AS ourstore_model_number,
                    os."BrandName" AS ourstore_brand_name,
                    os."MyPrice" AS ourstore_my_price,
                    os."Currency" AS ourstore_currency,
                    os."MainImage" AS ourstore_image,
                    os."Cost" AS ourstore_cost,
                    os."About" AS ourstore_about
                FROM 
                    product_product p
                JOIN 
                    product_ourstoreproduct os
                ON 
                    (p."ModelNumber" = os."ModelNumber"
                    OR p."ModelNumber" LIKE TRIM(BOTH FROM os."ModelNumber"))
                    --OR SIMILARITY(p."ModelNumber", os."ModelNumber") > 0.8
                    --OR SIMILARITY(p."ProductName", os."ProductName") > 0.9)
                    
                JOIN 
                    product_vendor v  -- Join Vendor table
                ON 
                    p."VendorCode_id" = v."VendorCode"  -- Use VendorCode_id for the foreign key
                WHERE 
                    os."MyPrice" > COALESCE(NULLIF(p."Offer", 0), p."RegularPrice")

            '''

            # Dynamic filters
            query_conditions = []
            query_params = []

            if brand_name:
                query_conditions.append('LOWER(p."BrandName") = LOWER(%s) AND LOWER(os."BrandName") = LOWER(%s)')
                query_params.extend([brand_name, brand_name])

            if category_name:
                query_conditions.append('p."CategoryName" ILIKE %s')
                query_params.append(f'%{category_name}%')

            if product_name:
                query_conditions.append('os."ProductName" ILIKE %s')
                query_params.append(f'%{product_name}%')

            if query_conditions:
                query += " AND " + " AND ".join(query_conditions)

            with connection.cursor() as cursor:
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                model_number_result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                print(f"SQL Query Result Count: {len(model_number_result)}")

            # Prepare results for model number matches
            product_map = {}
            for product in model_number_result:
                sku = product['ourstore_sku']
                if sku not in product_map:
                    product_map[sku] = {
                        "ProductName": product['ourstore_product_name'],
                        "SKU": product['ourstore_sku'],
                        "MyPrice": product['ourstore_my_price'],
                        "ModelNumber": product['ourstore_model_number'],
                        "Currency": product['ourstore_currency'],
                        "MainImage": product['ourstore_image'],
                        "Cost": product['ourstore_cost'],
                        "Brand": product['ourstore_brand_name'],
                        "About": [product['ourstore_about']],
                        "match_by": "ModelNumber",
                        "VendorsWithLowerPrice": [], 
                    }

                # Functions for calculating additional keys
                def get_stock(obj):
                    return "Instock" if obj['product_stock'] else "Out of stock"

                def get_discounted_price(obj):
                    return obj['product_offer_price'] if obj['product_offer_price'] else 0

                def get_regular_price(obj):
                    return obj['product_regular_price']

                def get_price_match(our_product, obj):
                    retailer_price = obj['product_offer_price'] if obj['product_offer_price'] else obj['product_regular_price']
                    if our_product and retailer_price:
                        price_difference = our_product['MyPrice'] - retailer_price
                        price_match_percentage = (price_difference / our_product['MyPrice']) * 100 if our_product['MyPrice'] != 0 else 0
                        return round(price_match_percentage, 2)
                    return 0

                def get_net_match(our_product, obj):
                    retailer_price = obj['product_offer_price'] if obj['product_offer_price'] else obj['product_regular_price']
                    if our_product and retailer_price and our_product['Cost']:
                        net_margin = (retailer_price - our_product['Cost']) / our_product['Cost'] * 100
                        return round(net_margin, 2)
                    return 0

                def get_discount(obj):
                    if obj['product_offer_price'] and obj['product_regular_price'] and obj['product_regular_price'] != 0:
                        discount_percentage = round(((obj['product_regular_price'] - obj['product_offer_price']) / obj['product_regular_price']) * 100, 2)
                        return discount_percentage
                    return 0
                

                if product['ourstore_my_price'] > (product['product_offer_price'] or product['product_regular_price']):
                    product_map[sku]["VendorsWithLowerPrice"].append({
                        "VendorName": product['vendor_name'],  # Fetch the correct VendorName
                        "SKU": product['product_sku'],
                        "ModelNumber": product['product_model_number'],
                        "Price": product['product_offer_price'] or product['product_regular_price'],  # Offer first, then RegularPrice
                        "Currency": product['product_currency'],
                        "ProductName": product['product_product_name'],
                        "Stock": get_stock(product),
                        "DiscountedPrice": get_discounted_price(product),
                        "RegularPrice": get_regular_price(product),
                        "PriceMatch": get_price_match(product_map[sku], product),
                        "NetMatch": get_net_match(product_map[sku], product),
                        "Discount": get_discount(product),
                    })


            # Filter out products with empty "VendorsWithHigherPrice"
            total_matches_before_filter = len(product_map)  # Include all products in the count
            print(f"Total Matches Before Filter: {total_matches_before_filter}")
            filtered_results = [product for product in product_map.values() if product["VendorsWithLowerPrice"]]

            # Convert dict to list for response
            final_result = filtered_results

            # Apply pagination
            paginator = Paginator(final_result, page_size)
            page_data = paginator.page(page)

            # Prepare the response
            response_data = {
                'products': page_data.object_list,
                'page': page,
                'page_size': page_size,
                'next_page': page_data.has_next(),
                'previous_page': page_data.has_previous(),
                'total_matches': len(final_result)
            }

            return Response(response_data)

        except EmptyPage:
            return Response({'message': 'Page not found'}, status=404)

        except Exception as e:
            return Response({'message': str(e)}, status=404)






class IntelligenceProductPriceEqual(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        try:
            # Get user input parameters (optional)
            brand_name = request.GET.get('brand_name', None)
            category_name = request.GET.get('category_name', None)
            product_name = request.GET.get('product_name', None)

            # Get pagination parameters
            page_size = int(request.GET.get('page_size', 5))  # Default to 5 products per page
            page = int(request.GET.get('page', 1))  # Default to page 1

            # Base SQL query for ModelNumber matching
            query = '''
                SELECT 
                    p."ProductCode" AS product_product_code,
                    p."ProductName" AS product_product_name,
                    p."SKU" AS product_sku,
                    p."ModelNumber" AS product_model_number,
                    p."BrandName" AS product_brand_name,
                    p."RegularPrice" AS product_regular_price,
                    p."Offer" AS product_offer_price,
                    p."Currency" AS product_currency,
                    p."StockAvailability" AS product_stock,
                    v."VendorName" AS vendor_name,  -- Fetch VendorName from Vendor model
                    os."ProductCode" AS ourstore_product_code,
                    os."ProductName" AS ourstore_product_name,
                    os."SKU" AS ourstore_sku,
                    os."ModelNumber" AS ourstore_model_number,
                    os."BrandName" AS ourstore_brand_name,
                    os."MyPrice" AS ourstore_my_price,
                    os."Currency" AS ourstore_currency,
                    os."MainImage" AS ourstore_image,
                    os."Cost" AS ourstore_cost,
                    os."About" AS ourstore_about
                FROM 
                    product_product p
                JOIN 
                    product_ourstoreproduct os
                ON 
                    (p."ModelNumber" = os."ModelNumber"
                    OR p."ModelNumber" LIKE TRIM(BOTH FROM os."ModelNumber"))

                JOIN 
                    product_vendor v  -- Join Vendor table
                ON 
                    p."VendorCode_id" = v."VendorCode"  -- Use VendorCode_id for the foreign key
                WHERE 
                    os."MyPrice" = COALESCE(NULLIF(p."Offer", 0), p."RegularPrice")

            '''

            # Dynamic filters
            query_conditions = []
            query_params = []

            if brand_name:
                query_conditions.append('LOWER(p."BrandName") = LOWER(%s) AND LOWER(os."BrandName") = LOWER(%s)')
                query_params.extend([brand_name, brand_name])

            if category_name:
                query_conditions.append('p."CategoryName" ILIKE %s')
                query_params.append(f'%{category_name}%')

            if product_name:
                query_conditions.append('os."ProductName" ILIKE %s')
                query_params.append(f'%{product_name}%')

            if query_conditions:
                query += " AND " + " AND ".join(query_conditions)

            with connection.cursor() as cursor:
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                model_number_result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                print(f"SQL Query Result Count: {len(model_number_result)}")

            # Prepare results for model number matches
            product_map = {}
            for product in model_number_result:
                sku = product['ourstore_sku']
                if sku not in product_map:
                    product_map[sku] = {
                        "ProductName": product['ourstore_product_name'],
                        "SKU": product['ourstore_sku'],
                        "MyPrice": product['ourstore_my_price'],
                        "ModelNumber": product['ourstore_model_number'],
                        "Currency": product['ourstore_currency'],
                        "MainImage": product['ourstore_image'],
                        "Cost": product['ourstore_cost'],
                        "Brand": product['ourstore_brand_name'],
                        "About": [product['ourstore_about']],
                        "match_by": "ModelNumber",
                        "VendorsWithEqualPrice": [], 
                    }
                
                # Functions for calculating additional keys
                def get_stock(obj):
                    return "Instock" if obj['product_stock'] else "Out of stock"

                def get_discounted_price(obj):
                    return obj['product_offer_price'] if obj['product_offer_price'] else 0

                def get_regular_price(obj):
                    return obj['product_regular_price']

                def get_price_match(our_product, obj):
                    retailer_price = obj['product_offer_price'] if obj['product_offer_price'] else obj['product_regular_price']
                    if our_product and retailer_price:
                        price_difference = our_product['MyPrice'] - retailer_price
                        price_match_percentage = (price_difference / our_product['MyPrice']) * 100 if our_product['MyPrice'] != 0 else 0
                        return round(price_match_percentage, 2)
                    return 0

                def get_net_match(our_product, obj):
                    retailer_price = obj['product_offer_price'] if obj['product_offer_price'] else obj['product_regular_price']
                    if our_product and retailer_price and our_product['Cost']:
                        net_margin = (retailer_price - our_product['Cost']) / our_product['Cost'] * 100
                        return round(net_margin, 2)
                    return 0

                def get_discount(obj):
                    if obj['product_offer_price'] and obj['product_regular_price'] and obj['product_regular_price'] != 0:
                        discount_percentage = round(((obj['product_regular_price'] - obj['product_offer_price']) / obj['product_regular_price']) * 100, 2)
                        return discount_percentage
                    return 0


                if product['ourstore_my_price'] == (product['product_offer_price'] or product['product_regular_price']):
                    product_map[sku]["VendorsWithEqualPrice"].append({
                        "VendorName": product['vendor_name'],  # Fetch the correct VendorName
                        "SKU": product['product_sku'],
                        "ModelNumber": product['product_model_number'],
                        "Price": product['product_offer_price'] or product['product_regular_price'],  # Offer first, then RegularPrice
                        "Currency": product['product_currency'],
                        "ProductName": product['product_product_name'],
                        "Stock": get_stock(product),
                        "DiscountedPrice": get_discounted_price(product),
                        "RegularPrice": get_regular_price(product),
                        "PriceMatch": get_price_match(product_map[sku], product),
                        "NetMatch": get_net_match(product_map[sku], product),
                        "Discount": get_discount(product),
                    })


            # Filter out products with empty "VendorsWithHigherPrice"
            total_matches_before_filter = len(product_map)  # Include all products in the count
            print(f"Total Matches Before Filter: {total_matches_before_filter}")
            filtered_results = [product for product in product_map.values() if product["VendorsWithEqualPrice"]]

            # Convert dict to list for response
            final_result = filtered_results

            # Apply pagination
            paginator = Paginator(final_result, page_size)
            page_data = paginator.page(page)

            # Prepare the response
            response_data = {
                'products': page_data.object_list,
                'page': page,
                'page_size': page_size,
                'next_page': page_data.has_next(),
                'previous_page': page_data.has_previous(),
                'total_matches': len(final_result)
            }

            return Response(response_data)

        except EmptyPage:
            return Response({'message': 'Page not found'}, status=404)

        except Exception as e:
            return Response({'message': str(e)}, status=404)



class IntelligenceProductPriceDifference(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        try:
            # Get user input parameters (optional)
            brand_name = request.GET.get('brand_name', None)
            category_name = request.GET.get('category_name', None)
            product_name = request.GET.get('product_name', None)

            # Get pagination parameters
            page_size = int(request.GET.get('page_size', 5))  # Default to 5 products per page
            page = int(request.GET.get('page', 1))  # Default to page 1

            # Base SQL query for ModelNumber matching
            query = '''
                SELECT 
                    p."ProductCode" AS product_product_code,
                    p."ProductName" AS product_product_name,
                    p."SKU" AS product_sku,
                    p."ModelNumber" AS product_model_number,
                    p."BrandName" AS product_brand_name,
                    p."RegularPrice" AS product_regular_price,
                    p."Offer" AS product_offer_price,
                    p."Currency" AS product_currency,
                    p."StockAvailability" AS product_stock,
                    v."VendorName" AS vendor_name,  -- Fetch VendorName from Vendor model
                    os."ProductCode" AS ourstore_product_code,
                    os."ProductName" AS ourstore_product_name,
                    os."SKU" AS ourstore_sku,
                    os."ModelNumber" AS ourstore_model_number,
                    os."BrandName" AS ourstore_brand_name,
                    os."MyPrice" AS ourstore_my_price,
                    os."Currency" AS ourstore_currency,
                    os."MainImage" AS ourstore_image,
                    os."Cost" AS ourstore_cost,
                    os."About" AS ourstore_about
                FROM 
                    product_product p
                JOIN 
                    product_ourstoreproduct os
                ON 
                    (p."ModelNumber" = os."ModelNumber"
                    OR p."ModelNumber" LIKE TRIM(BOTH FROM os."ModelNumber"))
                JOIN 
                    product_vendor v  -- Join Vendor table
                ON 
                    p."VendorCode_id" = v."VendorCode"  -- Use VendorCode_id for the foreign key
                WHERE
                    os."MyPrice" >= (COALESCE(p."Offer", p."RegularPrice") - 10) 
                    AND os."MyPrice" <= (COALESCE(p."Offer", p."RegularPrice") + 10)

            '''

            # Dynamic filters
            query_conditions = []
            query_params = []

            if brand_name:
                query_conditions.append('LOWER(p."BrandName") = LOWER(%s) AND LOWER(os."BrandName") = LOWER(%s)')
                query_params.extend([brand_name, brand_name])

            if category_name:
                query_conditions.append('p."CategoryName" ILIKE %s')
                query_params.append(f'%{category_name}%')

            if product_name:
                query_conditions.append('os."ProductName" ILIKE %s')
                query_params.append(f'%{product_name}%')

            if query_conditions:
                query += " AND " + " AND ".join(query_conditions)

            with connection.cursor() as cursor:
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                model_number_result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                print(f"SQL Query Result Count: {len(model_number_result)}")

            # Prepare results for model number matches
            product_map = {}
            for product in model_number_result:
                sku = product['ourstore_sku']
                if sku not in product_map:
                    product_map[sku] = {
                        "ProductName": product['ourstore_product_name'],
                        "SKU": product['ourstore_sku'],
                        "MyPrice": product['ourstore_my_price'],
                        "ModelNumber": product['ourstore_model_number'],
                        "Currency": product['ourstore_currency'],
                        "MainImage": product['ourstore_image'],
                        "Cost": product['ourstore_cost'],
                        "Brand": product['ourstore_brand_name'],
                        "About": [product['ourstore_about']],
                        "match_by": "ModelNumber",
                        "Vendors": [], 
                    }
                
                # Functions for calculating additional keys
                def get_stock(obj):
                    return "Instock" if obj['product_stock'] else "Out of stock"

                def get_discounted_price(obj):
                    return obj['product_offer_price'] if obj['product_offer_price'] else 0

                def get_regular_price(obj):
                    return obj['product_regular_price']

                def get_price_match(our_product, obj):
                    retailer_price = obj['product_offer_price'] if obj['product_offer_price'] else obj['product_regular_price']
                    if our_product and retailer_price:
                        price_difference = our_product['MyPrice'] - retailer_price
                        price_match_percentage = (price_difference / our_product['MyPrice']) * 100 if our_product['MyPrice'] != 0 else 0
                        return round(price_match_percentage, 2)
                    return 0

                def get_net_match(our_product, obj):
                    retailer_price = obj['product_offer_price'] if obj['product_offer_price'] else obj['product_regular_price']
                    if our_product and retailer_price and our_product['Cost']:
                        net_margin = (retailer_price - our_product['Cost']) / our_product['Cost'] * 100
                        return round(net_margin, 2)
                    return 0

                def get_discount(obj):
                    if obj['product_offer_price'] and obj['product_regular_price'] and obj['product_regular_price'] != 0:
                        discount_percentage = round(((obj['product_regular_price'] - obj['product_offer_price']) / obj['product_regular_price']) * 100, 2)
                        return discount_percentage
                    return 0
                

                if product['ourstore_my_price'] > ((product['product_offer_price'] or product['product_regular_price']) - 10) \
                and product['ourstore_my_price'] < ((product['product_offer_price'] or product['product_regular_price']) + 10):
                    product_map[sku]["Vendors"].append({
                        "VendorName": product['vendor_name'],  # Fetch the correct VendorName
                        "SKU": product['product_sku'],
                        "ModelNumber": product['product_model_number'],
                        "Price": product['product_offer_price'] or product['product_regular_price'],  # Offer first, then RegularPrice
                        "Currency": product['product_currency'],
                        "ProductName": product['product_product_name'],
                        "Stock": get_stock(product),
                        "DiscountedPrice": get_discounted_price(product),
                        "RegularPrice": get_regular_price(product),
                        "PriceMatch": get_price_match(product_map[sku], product),
                        "NetMatch": get_net_match(product_map[sku], product),
                        "Discount": get_discount(product),
                    })


            # Filter out products with empty "VendorsWithHigherPrice"
            total_matches_before_filter = len(product_map)  # Include all products in the count
            print(f"Total Matches Before Filter: {total_matches_before_filter}")
            filtered_results = [product for product in product_map.values() if product["Vendors"]]

            # Convert dict to list for response
            final_result = filtered_results

            # Apply pagination
            paginator = Paginator(final_result, page_size)
            page_data = paginator.page(page)

            # Prepare the response
            response_data = {
                'products': page_data.object_list,
                'page': page,
                'page_size': page_size,
                'next_page': page_data.has_next(),
                'previous_page': page_data.has_previous(),
                'total_matches': len(final_result)
            }

            return Response(response_data)

        except EmptyPage:
            return Response({'message': 'Page not found'}, status=404)

        except Exception as e:
            return Response({'message': str(e)}, status=404)


    


class ProductCountHigher(generics.GenericAPIView):
    """
    API View to return the total count of distinct products based on SKU, 
    including higher-priced products.
    """

    def get(self, request, *args, **kwargs):
        try:
            # SQL query to count distinct products and higher-priced products in one query
            query = '''
                SELECT 
                    COUNT(DISTINCT os."SKU") AS total_products,  -- Total distinct products
                    COUNT(DISTINCT CASE 
                        WHEN os."MyPrice" > COALESCE(NULLIF(p."Offer", 0), p."RegularPrice") 
                        THEN os."SKU" 
                    END) AS higher_products  -- Count distinct higher-priced products
                FROM 
                    product_product p
                JOIN 
                    product_ourstoreproduct os
                ON 
                    (p."ModelNumber" = os."ModelNumber"
                    OR p."ModelNumber" LIKE TRIM(BOTH FROM os."ModelNumber"))
                JOIN 
                    product_vendor v  -- Join Vendor table
                ON 
                    p."VendorCode_id" = v."VendorCode";  -- Use VendorCode_id for the foreign key
            '''

            # Execute the raw SQL query
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                total_products = result[0] if result else 0
                higher_products = result[1] if result else 0

            # Calculate the difference and percentages
            difference = total_products - higher_products

            if total_products > 0:
                higher_products_percentage = (higher_products / total_products) * 100
                difference_percentage = (difference / total_products) * 100
            else:
                higher_products_percentage = 0
                difference_percentage = 0

            # Return the results in the response
            return Response({
                'total_products_count': total_products,
                'higher_products_count': higher_products,
                'difference_count': difference,
                'higher_products_percentage': round(higher_products_percentage, 2),
                'difference_percentage': round(difference_percentage, 2),
                'name': 'High Price SKUs'
            })

        except Exception as e:
            # Handle errors and return an appropriate response
            return Response({'error': str(e)}, status=500)

        



class ProductCountLower(generics.GenericAPIView):
    """
    API View to return the total count of distinct products based on SKU, 
    including higher-priced products.
    """

    def get(self, request, *args, **kwargs):
        try:
            # SQL query to count distinct products and higher-priced products in one query
            query = '''
                SELECT 
                    COUNT(DISTINCT os."SKU") AS total_products,  -- Total distinct products
                    COUNT(DISTINCT CASE 
                        WHEN os."MyPrice" < COALESCE(NULLIF(p."Offer", 0), p."RegularPrice") 
                        THEN os."SKU" 
                    END) AS lower_products  -- Count distinct lower-priced products
                FROM 
                    product_product p
                JOIN 
                    product_ourstoreproduct os
                ON 
                    (p."ModelNumber" = os."ModelNumber"
                    OR p."ModelNumber" LIKE TRIM(BOTH FROM os."ModelNumber"))
                JOIN 
                    product_vendor v  -- Join Vendor table
                ON 
                    p."VendorCode_id" = v."VendorCode";  -- Use VendorCode_id for the foreign key
            '''

            # Execute the raw SQL query
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                total_products = result[0] if result else 0
                lower_products = result[1] if result else 0

            # Calculate the difference and percentages
            difference = total_products - lower_products

            if total_products > 0:
                lower_products_percentage = (lower_products / total_products) * 100
                difference_percentage = (difference / total_products) * 100
            else:
                lower_products_percentage = 0
                difference_percentage = 0

            # Return the results in the response
            return Response({
                'total_products_count': total_products,
                'lower_products_count': lower_products,
                'difference_count': difference,
                'lower_products_percentage': round(lower_products_percentage, 2),
                'difference_percentage': round(difference_percentage, 2),
                'name': 'Low Price SKUs'
            })

        except Exception as e:
            # Handle errors and return an appropriate response
            return Response({'error': str(e)}, status=500)

        


class ProductCountEqual(generics.GenericAPIView):
    """
    API View to return the total count of distinct products based on SKU, 
    including higher-priced products.
    """

    def get(self, request, *args, **kwargs):
        try:
            # SQL query to count distinct products and higher-priced products in one query
            query = '''
                SELECT 
                    COUNT(DISTINCT os."SKU") AS total_products,  -- Total distinct products
                    COUNT(DISTINCT CASE 
                        WHEN os."MyPrice" = COALESCE(NULLIF(p."Offer", 0), p."RegularPrice") 
                        THEN os."SKU" 
                    END) AS equal_products  -- Count distinct higher-priced products
                FROM 
                    product_product p
                JOIN 
                    product_ourstoreproduct os
                ON 
                    (p."ModelNumber" = os."ModelNumber"
                    OR p."ModelNumber" LIKE TRIM(BOTH FROM os."ModelNumber"))
                JOIN 
                    product_vendor v  -- Join Vendor table
                ON 
                    p."VendorCode_id" = v."VendorCode";  -- Use VendorCode_id for the foreign key
            '''

            # Execute the raw SQL query
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                total_products = result[0] if result else 0
                equal_products = result[1] if result else 0

            # Calculate the difference and percentages
            difference = total_products - equal_products

            if total_products > 0:
                equal_products_percentage = (equal_products / total_products) * 100
                difference_percentage = (difference / total_products) * 100
            else:
                equal_products_percentage = 0
                difference_percentage = 0

            # Return the results in the response
            return Response({
                'total_products_count': total_products,
                'equal_products_count': equal_products,
                'difference_count': difference,
                'equal_products_percentage': round(equal_products_percentage, 2),
                'difference_percentage': round(difference_percentage, 2),
                'name': 'Equal Price SKUs'
            })

        except Exception as e:
            # Handle errors and return an appropriate response
            return Response({'error': str(e)}, status=500)
        



class ProductCountRange(generics.GenericAPIView):
    """
    API View to return the total count of distinct products based on SKU, 
    including higher-priced products.
    """

    def get(self, request, *args, **kwargs):
        try:
            # SQL query to count distinct products and higher-priced products in one query
            query = '''
                SELECT 
                    COUNT(DISTINCT os."SKU") AS total_products,  -- Total distinct products
                    COUNT(DISTINCT CASE 
                        WHEN os."MyPrice" >= (COALESCE(p."Offer", p."RegularPrice") - 10) AND os."MyPrice" <= (COALESCE(p."Offer", p."RegularPrice") + 10) 
                        THEN os."SKU" 
                    END) AS range_products  -- Count distinct higher-priced products
                FROM 
                    product_product p
                JOIN 
                    product_ourstoreproduct os
                ON 
                    (p."ModelNumber" = os."ModelNumber"
                    OR p."ModelNumber" LIKE TRIM(BOTH FROM os."ModelNumber"))
                JOIN 
                    product_vendor v  -- Join Vendor table
                ON 
                    p."VendorCode_id" = v."VendorCode";  -- Use VendorCode_id for the foreign key
            '''

            # Execute the raw SQL query
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                total_products = result[0] if result else 0
                range_products = result[1] if result else 0

            # Calculate the difference and percentages
            difference = total_products - range_products

            if total_products > 0:
                range_products_percentage = (range_products / total_products) * 100
                difference_percentage = (difference / total_products) * 100
            else:
                range_products_percentage = 0
                difference_percentage = 0

            # Return the results in the response
            return Response({
                'total_products_count': total_products,
                'range_products_count': range_products,
                'difference_count': difference,
                'range_products_percentage': round(range_products_percentage, 2),
                'difference_percentage': round(difference_percentage, 2),
                'name': 'Average Price SKUs'
            })

        except Exception as e:
            # Handle errors and return an appropriate response
            return Response({'error': str(e)}, status=500)





