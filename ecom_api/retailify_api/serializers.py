from rest_framework import serializers
from api.product.models import Vendor, Catalogue, Category, Product, Review, Image, OurStoreProduct
from decimal import Decimal

# class VendorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Vendor
#         fields = '__all__'

class CatalogueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catalogue
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class OurStoreProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurStoreProduct
        fields = '__all__'




############## CUSTOM SERIALIZERS #############################
#FOR custom-products view
class CustomProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ProductName')
    url = serializers.CharField(source='MainImage')
    Brand = serializers.CharField(source='BrandName')
    category = serializers.CharField(source='CategoryName')


    my_price = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    net_margin = serializers.SerializerMethodField()
    about = serializers.SerializerMethodField()


    class Meta:
        model = OurStoreProduct
        fields = ['name', 'url', 'Brand', 'category', 'my_price', 'cost', 'net_margin', 'about']
        #fields = ['my_price', 'cost', 'net_margin']

    #THIS IS WRONG CALCULATION WISE
    def get_my_price(self, obj):
        return obj.MyPrice
    
    #THIS IS WRONG CALCULATION WISE
    def get_cost(self, obj):
        return obj.MyPrice * Decimal('0.75') if obj.MyPrice else None

    #THIS IS WRONG CALCULATION WISE
    def get_net_margin(self, obj):
        if obj.MyPrice and obj.MyPrice:
            cost = self.get_cost(obj)
            return round(((obj.MyPrice - cost) / cost) * 100, 2)
        return None

    def get_about(self, obj):
        if obj.About:
            return [obj.About]
        return []

    # def get_about(self, obj):
    #     # Example of splitting the about text by periods.
    #     # You can modify this based on how the text is structured in the database.
    #     if obj.About:
    #         return obj.About.split('\n')  # Split by sentence, period followed by space
    #     return [""]  # Default value if 'About' is empty or None
    

#Retailer Serializer
class VendorSerializer(serializers.ModelSerializer):
    # Correcting the VendorName reference
    vendor = serializers.CharField(source='VendorCode.VendorName')  # Access the related Vendor's name
    discounted_price = serializers.SerializerMethodField()
    regular_price = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    price_match = serializers.SerializerMethodField()
    net_match = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='ProductName')
    sku = serializers.CharField(source='SKU')

    class Meta:
        model = Product
        fields = ['vendor', 'discounted_price', 'regular_price', 'stock', 'color', 'price_match', 'net_match', 'discount', 'product_name', 'sku', 'Currency', 'BrandName', 'CategoryName']

    def get_stock(self, obj):
        return "Instock" if obj.StockAvailability else "Out of stock"
    
    def get_discounted_price(self, obj):
        # Return the Offer price if it's non-zero, otherwise 0
        return obj.Offer if obj.Offer else 0
    
    def get_regular_price(self, obj):
        return obj.RegularPrice

    def get_color(self, obj):
        return "#01821b" if obj.StockAvailability else "#ff0000"

    def get_price_match(self, obj):
        """
        Price match is the difference between your store price and retailer price.
        Use Offer price if available, otherwise use RegularPrice.
        """
        our_product = self.context.get('our_product')
        retailer_price = obj.Offer if obj.Offer else obj.RegularPrice
        if our_product and retailer_price:
            price_difference = our_product.MyPrice - retailer_price
            price_match_percentage = (price_difference / our_product.MyPrice) * 100 if our_product.MyPrice != 0 else 0
            return round(price_match_percentage, 2)
        return 0

    def get_net_match(self, obj):
        """
        Net match is the margin difference between your cost and retailer price.
        Use Offer price if available, otherwise use RegularPrice.
        """
        our_product = self.context.get('our_product')
        retailer_price = obj.Offer if obj.Offer else obj.RegularPrice
        if our_product and retailer_price and our_product.Cost:
            net_margin = (retailer_price - our_product.Cost) / our_product.Cost * 100
            return round(net_margin, 2)
        return 0

    def get_discount(self, obj):
        if obj.Offer and obj.RegularPrice and obj.RegularPrice != 0:
            discount_percentage = round(float(((obj.RegularPrice - obj.Offer) / obj.RegularPrice) * 100), 2)
            return discount_percentage
        return 0


class ProductDetailsByCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField()
    total_price = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_products = serializers.IntegerField()

    class Meta:
        model = Category
        fields = ['category_name', 'total_price', 'total_products']



# class CountBrandProductCategorySerializer(serializers.ModelSerializer):
#     brand_count = serializers.IntegerField()
#     category_count = serializers.IntegerField()
#     product_count = serializers.IntegerField()



