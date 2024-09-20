from rest_framework import generics
from rest_framework.views import APIView
from api.product.models import Vendor, Catalogue, Category, Product, Review, Image
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
    """
    Compare products between the Product and OurStoreProduct tables based on product names with pagination.
    """
    serializer_class = VendorSerializer

    def process_product(self, our_product):
        # Approximate matching using TrigramSimilarity on the product name
        matching_products = Product.objects.annotate(
            similarity=TrigramSimilarity(F('ProductName'), our_product.ProductName.lower())
        ).annotate(
            similarity_rounded=Round(F('similarity'), 2)  # Round similarity score for better accuracy
        ).filter(
            Q(ProductName__icontains=our_product.ProductName.lower()) |  # Prioritize exact matches
            Q(similarity_rounded__gt=0.29)  # Increase similarity threshold for relevance
        ).order_by('-similarity_rounded')

        if matching_products.exists():
            vendor_products = []
            for product in matching_products:
                serializer = VendorSerializer(product, context={'our_product': our_product})  # Pass our product here
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
                    'about': [our_product.About]
                },
                "retailer_products": vendor_products
            }
            return comparison
        return None

    def get(self, request, *args, **kwargs):
        # Get pagination parameters
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)  # Default to 10 items per page

        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)

        # Fetch all the products from OurStoreProduct
        our_store_products = OurStoreProduct.objects.all()

        # Apply price filtering if min_price or max_price is provided
        if min_price is not None:
            our_store_products = our_store_products.filter(MyPrice__gte=min_price)
        if max_price is not None:
            our_store_products = our_store_products.filter(MyPrice__lte=max_price)

        # Order by ProductCode for consistency with pagination
        our_store_products = our_store_products.order_by('ProductCode')

        # Paginate results
        paginator = Paginator(our_store_products, page_size)
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
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
            paginated_categories = paginator.page(paginator.num_pages)

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
            paginated_brands = paginator.page(paginator.num_pages)

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
    



# class IntelligenceProductPriceView(generics.GenericAPIView):

#     def get(self, request, *args, **kwargs):
#         # Get the product name from user input (query parameter)
#         product_name = request.GET.get('product_name', None)

#         if not product_name:
#             return Response({"error": "Product name is required."}, status=400)

#         # Preprocess product name for case-insensitive filtering and trigram
#         lower_product_name = product_name.lower()

#         # Fetch all matching OurStoreProduct using TrigramSimilarity and filtering by product name
#         our_store_products = (
#             OurStoreProduct.objects
#             .annotate(similarity=TrigramSimilarity(F('ProductName'), lower_product_name))
#             .annotate(similarity_rounded=Round(F('similarity'), 2))  # Round the similarity
#             .filter(
#                 Q(ProductName__icontains=product_name) |  # Prioritize exact matches first
#                 Q(similarity_rounded__gt=0.2)  # Increase similarity threshold to reduce irrelevant matches
#             )
#             .order_by('-similarity_rounded')  # Order by highest rounded similarity
#         )

#         if not our_store_products.exists():
#             return Response({"error": "No similar products found in our store."}, status=404)

#         # Iterate over the store products to fetch the vendors with lower price
#         results = []
#         for our_store_product in our_store_products:
#             my_price = our_store_product.MyPrice
#             our_similarity = round(our_store_product.similarity, 2)  # Get similarity for OurStoreProduct

#             # Fetch all vendors with a similar product name who have a lower price than MyPrice
#             vendors_with_lower_price = (
#                 Product.objects
#                 .annotate(similarity=TrigramSimilarity(F('ProductName'), lower_product_name))
#                 .annotate(similarity_rounded=Round(F('similarity'), 2))  # Round the similarity
#                 .filter(
#                     Q(ProductName__icontains=product_name) |  # Prioritize exact matches for vendors too
#                     Q(similarity_rounded__gt=0.2)  # Increase similarity threshold for vendors as well
#                 )
#                 .filter(Q(Offer__lt=my_price) | Q(RegularPrice__lt=my_price))
#                 .values('VendorCode__VendorName', 'Offer', 'RegularPrice', 'ProductName', 'similarity_rounded')  # Fetch similarity
#                 .order_by('-similarity_rounded')  # Order by similarity
#             )

#             # Filter out vendors with similarity lower than the threshold
#             vendor_data = []
#             for vendor in vendors_with_lower_price:
#                 if vendor['similarity_rounded'] > 0.2:  # Ensure vendors with similarity > 0.3 only
#                     vendor_data.append({
#                         'VendorName': vendor['VendorCode__VendorName'],
#                         'Price': vendor['Offer'] if vendor['Offer'] else vendor['RegularPrice'],
#                         'ProductName': vendor['ProductName'],
#                         'Similarity': vendor['similarity_rounded']  # Include and round similarity score for vendor products
#                     })

#             # Only include products where there are valid vendors with lower prices
#             if vendor_data:
#                 # Prepare the response data for each OurStoreProduct
#                 results.append({
#                     "ProductName": our_store_product.ProductName,  # Return the matched product name from OurStoreProduct
#                     "MyPrice": my_price,
#                     "Similarity": our_similarity,  # Include similarity for OurStoreProduct
#                     "VendorsWithLowerPrice": vendor_data
#                 })

#         return Response(results)


class IntelligenceProductPriceView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        # Get the product name, brand name, and category from user input (query parameters)
        product_name = request.GET.get('product_name', None)
        brand_name = request.GET.get('brand_name', None)
        category_name = request.GET.get('category_name', None)

        if not product_name:
            return Response({"error": "Product name is required."}, status=400)

        # Tokenize the product name into individual words
        product_name_tokens = product_name.lower().split()

        # Create a filtering condition that matches all tokens in the product name
        token_conditions = Q()
        for token in product_name_tokens:
            token_conditions &= Q(ProductName__icontains=token)

        # If brand name is provided, include it in the filtering condition
        if brand_name:
            token_conditions &= Q(BrandName__icontains=brand_name)

        # If category name is provided, include it in the filtering condition
        if category_name:
            token_conditions &= Q(CategoryName__icontains=category_name)

        # Fetch all matching OurStoreProduct using TrigramSimilarity and keyword filtering
        our_store_products = (
            OurStoreProduct.objects
            .annotate(similarity=TrigramSimilarity(F('ProductName'), Value(product_name)))
            .filter(token_conditions)  # Ensure all tokens, brand, and category are matched
            .order_by('-similarity')  # Order by similarity score
        )

        if not our_store_products.exists():
            return Response({"error": "No similar products found in our store."}, status=404)

        # Iterate over the store products to fetch vendors with lower price
        results = []
        for our_store_product in our_store_products:
            my_price = our_store_product.MyPrice
            our_similarity = round(our_store_product.similarity, 2)  # Get similarity for OurStoreProduct

            # Fetch all vendors with a similar product name who have a lower price than MyPrice
            vendors_with_lower_price = (
                Product.objects
                .annotate(similarity=TrigramSimilarity(F('ProductName'), Value(product_name)))
                .filter(token_conditions)  # Ensure all tokens, brand, and category are matched for vendors as well
                .filter(Q(Offer__lt=my_price) | Q(RegularPrice__lt=my_price))
                .values('VendorCode__VendorName', 'Offer', 'RegularPrice', 'ProductName', 'similarity')
                .order_by('-similarity')  # Order by similarity score
            )

            # Filter out vendors with similarity lower than the threshold
            vendor_data = []
            for vendor in vendors_with_lower_price:
                if vendor['similarity'] > 0.15:  # Ensure vendors with similarity > 0.2 only
                    vendor_data.append({
                        'VendorName': vendor['VendorCode__VendorName'],
                        'Price': vendor['Offer'] if vendor['Offer'] else vendor['RegularPrice'],
                        'ProductName': vendor['ProductName'],
                        'Similarity': round(vendor['similarity'], 2)  # Include and round similarity score for vendor products
                    })

            # Only include products where there are valid vendors with lower prices
            if vendor_data:
                results.append({
                    "ProductName": our_store_product.ProductName,  # Return the matched product name from OurStoreProduct
                    "MyPrice": my_price,
                    "Similarity": our_similarity,  # Include similarity for OurStoreProduct
                    "VendorsWithLowerPrice": vendor_data
                })

        return Response(results)



# class IntelligenceProductPriceDefault(generics.GenericAPIView):

#     def get(self, request, *args, **kwargs):
#         # Get the brand name, category, and product name from user input (query parameters)
#         brand_name = request.GET.get('brand_name', None)
#         category_name = request.GET.get('category_name', None)
#         product_name = request.GET.get('product_name', None)

#         # Validate that brand_name is provided
#         if not brand_name:
#             return Response({"error": "Brand name is required."}, status=400)

#         # Create a filtering condition that matches the brand name
#         filter_conditions = Q(BrandName__icontains=brand_name)

#         # If category name is provided, include it in the filtering condition
#         if category_name:
#             filter_conditions &= Q(CategoryName__icontains=category_name)

#         # If product name is provided, include it in the filtering condition
#         if product_name:
#             product_name_tokens = product_name.lower().split()  # Tokenize product name for more flexible matching
#             product_name_conditions = Q()
#             for token in product_name_tokens:
#                 product_name_conditions &= Q(ProductName__icontains=token)
#             filter_conditions &= product_name_conditions

#         # Fetch all matching OurStoreProduct using the brand name, category, and optional product name
#         our_store_products = (
#             OurStoreProduct.objects
#             .filter(filter_conditions)  # Match based on BrandName, CategoryName, and optionally ProductName
#             .order_by('ProductName')  # Optionally order by product name or other fields
#         )

#         if not our_store_products.exists():
#             return Response({"error": "No products found for the given brand, category, or product name."}, status=404)

#         # Iterate over the store products to fetch vendors with lower price
#         results = []
#         for our_store_product in our_store_products:
#             my_price = our_store_product.MyPrice

#             # Fetch all vendors with a similar brand name and optional category or product name who have a lower price than MyPrice
#             vendor_filter_conditions = Q(BrandName__icontains=brand_name) & (Q(Offer__lt=my_price) | Q(RegularPrice__lt=my_price))

#             # Apply category filter if provided
#             if category_name:
#                 vendor_filter_conditions &= Q(CategoryName__icontains=category_name)

#             # Apply product name filter if provided
#             if product_name:
#                 vendor_product_name_conditions = Q()
#                 for token in product_name_tokens:
#                     vendor_product_name_conditions &= Q(ProductName__icontains=token)
#                 vendor_filter_conditions &= vendor_product_name_conditions

#             vendor_products = (
#                 Product.objects
#                 .filter(vendor_filter_conditions)
#                 .values('VendorCode__VendorName', 'Offer', 'RegularPrice', 'ProductName')  # Fetch relevant fields
#                 .order_by('ProductName')  # Optionally order by product name
#             )

#             # Collect vendor data
#             vendor_data = []
#             for vendor in vendor_products:
#                 vendor_data.append({
#                     'VendorName': vendor['VendorCode__VendorName'],
#                     'Price': vendor['Offer'] if vendor['Offer'] else vendor['RegularPrice'],
#                     'ProductName': vendor['ProductName'],
#                 })

#             # Only include products where there are valid vendors with lower prices
#             if vendor_data:
#                 results.append({
#                     "ProductName": our_store_product.ProductName,  # Return the matched product name from OurStoreProduct
#                     "MyPrice": my_price,
#                     "VendorsWithLowerPrice": vendor_data
#                 })

#         return Response(results)




class IntelligenceProductPriceHigher(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        # Get the brand name, category, and product name from user input (query parameters)
        brand_name = request.GET.get('brand_name', None)
        category_name = request.GET.get('category_name', None)
        product_name = request.GET.get('product_name', None)

        # Validate that brand_name is provided
        if not brand_name:
            return Response({"error": "Brand name is required."}, status=400)

        # Create a filtering condition that matches the brand name
        filter_conditions = Q(BrandName__icontains=brand_name)

        # If category name is provided, include it in the filtering condition
        if category_name:
            filter_conditions &= Q(CategoryName__icontains=category_name)

        # If product name is provided, include it in the filtering condition
        if product_name:
            product_name_tokens = product_name.lower().split()  # Tokenize product name for more flexible matching
            product_name_conditions = Q()
            numeric_tokens = []
            
            for token in product_name_tokens:
                if token.isdigit():
                    numeric_tokens.append(token)  # Collect numeric tokens for strict matching
                else:
                    product_name_conditions &= Q(ProductName__icontains=token)
            
            filter_conditions &= product_name_conditions

        # Fetch all matching OurStoreProduct using the brand name, category, and optional product name
        our_store_products = (
            OurStoreProduct.objects
            .filter(filter_conditions)  # Match based on BrandName, CategoryName, and optionally ProductName
            .order_by('ProductName')  # Optionally order by product name or other fields
        )

        if not our_store_products.exists():
            return Response({"error": "No products found for the given brand, category, or product name."}, status=404)

        results = []

        for our_store_product in our_store_products:
            # Check if numeric tokens (model numbers) exactly match
            if product_name and numeric_tokens:
                product_name_lower = our_store_product.ProductName.lower()
                # Ensure all numeric tokens are present exactly
                if not all(f" {token} " in f" {product_name_lower} " for token in numeric_tokens):
                    continue  # Skip this product if it doesn't match all numeric tokens

            my_price = our_store_product.MyPrice

            # Fetch all vendors with a similar brand name and optional category or product name who have a lower price than MyPrice
            vendor_filter_conditions = Q(BrandName__icontains=brand_name) & (
                Q(Offer__lt=my_price) | Q(RegularPrice__lt=my_price)
            )

            # Apply category filter if provided
            if category_name:
                vendor_filter_conditions &= Q(CategoryName__icontains=category_name)

            # Apply product name filter if provided
            if product_name:
                vendor_product_name_conditions = Q()
                for token in product_name_tokens:
                    if token.isdigit():
                        vendor_product_name_conditions &= Q(ProductName__icontains=token)
                    else:
                        vendor_product_name_conditions &= Q(ProductName__icontains=token)
                vendor_filter_conditions &= vendor_product_name_conditions

            vendor_products = (
                Product.objects
                .filter(vendor_filter_conditions)
                .values('VendorCode__VendorName', 'Offer', 'RegularPrice', 'ProductName', 'Currency')  # Fetch relevant fields
                .order_by('ProductName')  # Optionally order by product name
            )

            # Collect vendor data where vendor price is lower than our price
            vendor_data = []
            for vendor in vendor_products:
                vendor_price = vendor['Offer'] if vendor['Offer'] else vendor['RegularPrice']
                
                # Ensure that the vendor price is indeed lower than `my_price`
                if vendor_price < my_price:
                    vendor_data.append({
                        'VendorName': vendor['VendorCode__VendorName'],
                        'Price': vendor_price,
                        'Currency': vendor['Currency'],
                        'ProductName': vendor['ProductName'],
                    })

            # Only include products where there are valid vendors with lower prices
            if vendor_data:
                results.append({
                    "ProductName": our_store_product.ProductName,  # Return the matched product name from OurStoreProduct
                    "MyPrice": my_price,
                    "Currency": our_store_product.Currency,
                    "VendorsWithLowerPrice": vendor_data
                })

        return Response(results)

    


class IntelligenceProductPriceLower(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        # Get the brand name, category, and product name from user input (query parameters)
        brand_name = request.GET.get('brand_name', None)
        category_name = request.GET.get('category_name', None)
        product_name = request.GET.get('product_name', None)

        # Validate that brand_name is provided
        if not brand_name:
            return Response({"error": "Brand name is required."}, status=400)

        # Create a filtering condition that matches the brand name
        filter_conditions = Q(BrandName__icontains=brand_name)

        # If category name is provided, include it in the filtering condition
        if category_name:
            filter_conditions &= Q(CategoryName__icontains=category_name)

        # If product name is provided, include it in the filtering condition
        if product_name:
            product_name_tokens = product_name.lower().split()  # Tokenize product name for more flexible matching
            product_name_conditions = Q()
            numeric_tokens = []
            
            for token in product_name_tokens:
                if token.isdigit():
                    numeric_tokens.append(token)  # Collect numeric tokens for strict matching
                else:
                    product_name_conditions &= Q(ProductName__icontains=token)
            
            filter_conditions &= product_name_conditions

        # Fetch all matching OurStoreProduct using the brand name, category, and optional product name
        our_store_products = (
            OurStoreProduct.objects
            .filter(filter_conditions)  # Match based on BrandName, CategoryName, and optionally ProductName
            .order_by('ProductName')  # Optionally order by product name or other fields
        )

        if not our_store_products.exists():
            return Response({"error": "No products found for the given brand, category, or product name."}, status=404)

        results = []

        for our_store_product in our_store_products:
            # Check if numeric tokens (model numbers) exactly match
            if product_name and numeric_tokens:
                product_name_lower = our_store_product.ProductName.lower()
                # Ensure all numeric tokens are present exactly
                if not all(f" {token} " in f" {product_name_lower} " for token in numeric_tokens):
                    continue  # Skip this product if it doesn't match all numeric tokens

            my_price = our_store_product.MyPrice

            # Fetch all vendors with a similar brand name and optional category or product name who have a price lower than MyPrice
            vendor_filter_conditions = Q(BrandName__icontains=brand_name) & (Q(Offer__lt=my_price) | Q(RegularPrice__lt=my_price))

            # Apply category filter if provided
            if category_name:
                vendor_filter_conditions &= Q(CategoryName__icontains=category_name)

            # Apply product name filter if provided
            if product_name:
                vendor_product_name_conditions = Q()
                for token in product_name_tokens:
                    if token.isdigit():
                        vendor_product_name_conditions &= Q(ProductName__icontains=token)
                    else:
                        vendor_product_name_conditions &= Q(ProductName__icontains=token)
                vendor_filter_conditions &= vendor_product_name_conditions

            vendor_products = (
                Product.objects
                .filter(vendor_filter_conditions)
                .values('VendorCode__VendorName', 'Offer', 'RegularPrice', 'ProductName', 'Currency')  # Fetch relevant fields
                .order_by('ProductName')  # Optionally order by product name
            )

            # Collect vendor data where vendor price is higher than our price
            vendor_data = []
            for vendor in vendor_products:
                vendor_price = vendor['Offer'] if vendor['Offer'] else vendor['RegularPrice']
                
                # Ensure that the vendor price is indeed higher than `my_price`
                if vendor_price > my_price:
                    vendor_data.append({
                        'VendorName': vendor['VendorCode__VendorName'],
                        'Price': vendor_price,
                        'Currency': vendor['Currency'],
                        'ProductName': vendor['ProductName'],
                    })

            # Only include products where there are valid vendors with higher prices
            if vendor_data:
                results.append({
                    "ProductName": our_store_product.ProductName,  # Return the matched product name from OurStoreProduct
                    "MyPrice": my_price,
                    "Currency": our_store_product.Currency,
                    "VendorsWithHigherPrice": vendor_data
                })

        return Response(results)

    


class IntelligenceProductPriceEqual(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        # Get the brand name, category, and product name from user input (query parameters)
        brand_name = request.GET.get('brand_name', None)
        category_name = request.GET.get('category_name', None)
        product_name = request.GET.get('product_name', None)

        # Validate that brand_name is provided
        if not brand_name:
            return Response({"error": "Brand name is required."}, status=400)

        # Create a filtering condition that matches the brand name
        filter_conditions = Q(BrandName__icontains=brand_name)

        # If category name is provided, include it in the filtering condition
        if category_name:
            filter_conditions &= Q(CategoryName__icontains=category_name)

        # If product name is provided, include it in the filtering condition
        if product_name:
            product_name_tokens = product_name.lower().split()  # Tokenize product name for more flexible matching
            product_name_conditions = Q()
            numeric_tokens = []

            for token in product_name_tokens:
                if token.isdigit():
                    numeric_tokens.append(token)  # Collect numeric tokens for strict matching
                else:
                    product_name_conditions &= Q(ProductName__icontains=token)

            filter_conditions &= product_name_conditions

        # Fetch all matching OurStoreProduct using the brand name, category, and optional product name
        our_store_products = (
            OurStoreProduct.objects
            .filter(filter_conditions)  # Match based on BrandName, CategoryName, and optionally ProductName
            .order_by('ProductName')  # Optionally order by product name or other fields
        )

        if not our_store_products.exists():
            return Response({"error": "No products found for the given brand, category, or product name."}, status=404)

        results = []

        for our_store_product in our_store_products:
            # Check if numeric tokens (model numbers) exactly match
            if product_name and numeric_tokens:
                product_name_lower = our_store_product.ProductName.lower()
                # Ensure all numeric tokens are present exactly
                if not all(f" {token} " in f" {product_name_lower} " for token in numeric_tokens):
                    continue  # Skip this product if it doesn't match all numeric tokens

            my_price = our_store_product.MyPrice

            # Fetch all vendors with a similar brand name and optional category or product name where prices are **equal** to MyPrice
            vendor_filter_conditions = Q(BrandName__icontains=brand_name) & (Q(Offer=my_price) | Q(RegularPrice=my_price))

            # Apply category filter if provided
            if category_name:
                vendor_filter_conditions &= Q(CategoryName__icontains=category_name)

            # Apply product name filter if provided
            if product_name:
                vendor_product_name_conditions = Q()
                for token in product_name_tokens:
                    if token.isdigit():
                        vendor_product_name_conditions &= Q(ProductName__icontains=token)
                    else:
                        vendor_product_name_conditions &= Q(ProductName__icontains=token)
                vendor_filter_conditions &= vendor_product_name_conditions

            vendor_products = (
                Product.objects
                .filter(vendor_filter_conditions)
                .values('VendorCode__VendorName', 'Offer', 'RegularPrice', 'ProductName', 'Currency')  # Fetch relevant fields
                .order_by('ProductName')  # Optionally order by product name
            )

            # Collect vendor data where vendor price is equal to our price
            vendor_data = []
            for vendor in vendor_products:
                vendor_price = vendor['Offer'] if vendor['Offer'] else vendor['RegularPrice']
                
                # Ensure that the vendor price is indeed equal to `my_price`
                if vendor_price == my_price:
                    vendor_data.append({
                        'VendorName': vendor['VendorCode__VendorName'],
                        'Price': vendor_price,
                        'Currency': vendor['Currency'],
                        'ProductName': vendor['ProductName'],
                    })

            # Only include products where there are valid vendors with equal prices
            if vendor_data:
                results.append({
                    "ProductName": our_store_product.ProductName,  # Return the matched product name from OurStoreProduct
                    "MyPrice": my_price,
                    "Currency": our_store_product.Currency,
                    "VendorsWithEqualPrice": vendor_data
                })

        return Response(results)

    


class IntelligenceProductPriceDifference(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        # Get the brand name, category, and product name from user input (query parameters)
        brand_name = request.GET.get('brand_name', None)
        category_name = request.GET.get('category_name', None)
        product_name = request.GET.get('product_name', None)

        # Validate that brand_name is provided
        if not brand_name:
            return Response({"error": "Brand name is required."}, status=400)

        # Create a filtering condition that matches the brand name
        filter_conditions = Q(BrandName__icontains=brand_name)

        # If category name is provided, include it in the filtering condition
        if category_name:
            filter_conditions &= Q(CategoryName__icontains=category_name)

        # If product name is provided, include it in the filtering condition
        if product_name:
            product_name_tokens = product_name.lower().split()  # Tokenize product name for more flexible matching
            product_name_conditions = Q()
            numeric_tokens = []

            for token in product_name_tokens:
                if token.isdigit():
                    numeric_tokens.append(token)  # Collect numeric tokens for strict matching
                else:
                    product_name_conditions &= Q(ProductName__icontains=token)

            filter_conditions &= product_name_conditions

        # Fetch all matching OurStoreProduct using the brand name, category, and optional product name
        our_store_products = (
            OurStoreProduct.objects
            .filter(filter_conditions)  # Match based on BrandName, CategoryName, and optionally ProductName
            .order_by('ProductName')  # Optionally order by product name or other fields
        )

        if not our_store_products.exists():
            return Response({"error": "No products found for the given brand, category, or product name."}, status=404)

        results = []

        for our_store_product in our_store_products:
            # Check if numeric tokens (model numbers) exactly match
            if product_name and numeric_tokens:
                product_name_lower = our_store_product.ProductName.lower()
                # Ensure all numeric tokens are present exactly
                if not all(f" {token} " in f" {product_name_lower} " for token in numeric_tokens):
                    continue  # Skip this product if it doesn't match all numeric tokens

            my_price = our_store_product.MyPrice

            # Fetch all vendors with a similar brand name and optional category or product name
            # where the price difference is within ±10 from MyPrice
            vendor_filter_conditions = Q(BrandName__icontains=brand_name) & (
                Q(Offer__gte=my_price - 10, Offer__lte=my_price + 10) |
                Q(RegularPrice__gte=my_price - 10, RegularPrice__lte=my_price + 10)
            )

            # Apply category filter if provided
            if category_name:
                vendor_filter_conditions &= Q(CategoryName__icontains=category_name)

            # Apply product name filter if provided
            if product_name:
                vendor_product_name_conditions = Q()
                for token in product_name_tokens:
                    if token.isdigit():
                        vendor_product_name_conditions &= Q(ProductName__icontains=token)
                    else:
                        vendor_product_name_conditions &= Q(ProductName__icontains=token)
                vendor_filter_conditions &= vendor_product_name_conditions

            vendor_products = (
                Product.objects
                .filter(vendor_filter_conditions)
                .values('VendorCode__VendorName', 'Offer', 'RegularPrice', 'ProductName', 'Currency')  # Fetch relevant fields
                .order_by('ProductName')  # Optionally order by product name
            )

            # Collect vendor data where price difference is within ±10
            vendor_data = []
            for vendor in vendor_products:
                vendor_price = vendor['Offer'] if vendor['Offer'] else vendor['RegularPrice']

                # Ensure that the vendor price is within ±10 of MyPrice
                if my_price - 10 <= vendor_price <= my_price + 10:
                    vendor_data.append({
                        'VendorName': vendor['VendorCode__VendorName'],
                        'Price': vendor_price,
                        'Currency': vendor['Currency'],
                        'ProductName': vendor['ProductName'],
                    })

            # Only include products where there are valid vendors with a price difference of ±10
            if vendor_data:
                results.append({
                    "ProductName": our_store_product.ProductName,  # Return the matched product name from OurStoreProduct
                    "MyPrice": my_price,
                    "Currency": our_store_product.Currency,
                    "VendorsWithPriceDifference": vendor_data
                })

        return Response(results)

    



class IntelligenceProductPriceLower(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        # Get the brand name, category, and product name from user input (query parameters)
        brand_name = request.GET.get('brand_name', None)
        category_name = request.GET.get('category_name', None)
        product_name = request.GET.get('product_name', None)

        # Validate that brand_name is provided
        if not brand_name:
            return Response({"error": "Brand name is required."}, status=400)

        # Create a filtering condition that matches the brand name
        filter_conditions = Q(BrandName__icontains=brand_name)

        # If category name is provided, include it in the filtering condition
        if category_name:
            filter_conditions &= Q(CategoryName__icontains=category_name)

        # If product name is provided, include it in the filtering condition
        if product_name:
            product_name_tokens = product_name.lower().split()  # Tokenize product name for more flexible matching
            product_name_conditions = Q()
            numeric_tokens = []

            for token in product_name_tokens:
                if token.isdigit():
                    numeric_tokens.append(token)  # Collect numeric tokens for strict matching
                else:
                    product_name_conditions &= Q(ProductName__icontains=token)

            filter_conditions &= product_name_conditions

        # Fetch all matching OurStoreProduct using the brand name, category, and optional product name
        our_store_products = (
            OurStoreProduct.objects
            .filter(filter_conditions)  # Match based on BrandName, CategoryName, and optionally ProductName
            .order_by('ProductName')  # Optionally order by product name or other fields
        )

        if not our_store_products.exists():
            return Response({"error": "No products found for the given brand, category, or product name."}, status=404)

        results = []

        for our_store_product in our_store_products:
            # Check if numeric tokens (model numbers) exactly match
            if product_name and numeric_tokens:
                product_name_lower = our_store_product.ProductName.lower()
                # Ensure all numeric tokens are present exactly
                if not all(f" {token} " in f" {product_name_lower} " for token in numeric_tokens):
                    continue  # Skip this product if it doesn't match all numeric tokens

            my_price = our_store_product.MyPrice

            # Fetch all vendors with a similar brand name and optional category or product name who have a higher price than MyPrice
            vendor_filter_conditions = Q(BrandName__icontains=brand_name) & (Q(Offer__gt=my_price) | Q(RegularPrice__gt=my_price))

            # Apply category filter if provided
            if category_name:
                vendor_filter_conditions &= Q(CategoryName__icontains=category_name)

            # Apply product name filter if provided
            if product_name:
                vendor_product_name_conditions = Q()
                for token in product_name_tokens:
                    if token.isdigit():
                        vendor_product_name_conditions &= Q(ProductName__icontains=token)
                    else:
                        vendor_product_name_conditions &= Q(ProductName__icontains=token)
                vendor_filter_conditions &= vendor_product_name_conditions

            # Fetch products from competitors that match strictly based on product name (no Pro/Plus mismatches)
            vendor_products = (
                Product.objects
                .filter(vendor_filter_conditions)
                .values('VendorCode__VendorName', 'Offer', 'RegularPrice', 'ProductName', 'Currency')  # Fetch relevant fields
                .order_by('ProductName')  # Optionally order by product name
            )

            # Collect vendor data
            vendor_data = []
            for vendor in vendor_products:
                # Stricter matching: Ensure the product name matches precisely (without Pro mismatches)
                if self.is_strict_model_match(our_store_product.ProductName, vendor['ProductName']):
                    vendor_data.append({
                        'VendorName': vendor['VendorCode__VendorName'],
                        'Price': vendor['Offer'] if vendor['Offer'] else vendor['RegularPrice'],
                        'Currency': vendor['Currency'],
                        'ProductName': vendor['ProductName'],
                    })

            # Only include products where there are valid vendors with higher prices
            if vendor_data:
                results.append({
                    "ProductName": our_store_product.ProductName,  # Return the matched product name from OurStoreProduct
                    "MyPrice": my_price,
                    "Currency": our_store_product.Currency,
                    "VendorsWithHigherPrice": vendor_data
                })

        return Response(results)

    def is_strict_model_match(self, our_product_name, vendor_product_name):
        """Ensure that both product names refer to the same model, ignoring slight variations."""
        # Normalize product names to lowercase
        our_product_tokens = set(our_product_name.lower().split())
        vendor_product_tokens = set(vendor_product_name.lower().split())

        # Model-specific tokens that need to match exactly
        model_keywords = {"pro", "max", "plus", "mini", "ultra"}

        # Ensure that the basic product name tokens (e.g., "iphone" and "15") match
        basic_tokens_match = our_product_tokens & vendor_product_tokens
        if not basic_tokens_match:
            return False

        # Ensure that if one product has a model-specific token (e.g., "Pro"), the other must also have it
        our_model_tokens = our_product_tokens & model_keywords
        vendor_model_tokens = vendor_product_tokens & model_keywords

        if our_model_tokens != vendor_model_tokens:
            return False

        return True



