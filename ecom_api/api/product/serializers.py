from rest_framework import serializers


from api.product.models import *


class CatalogueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Catalogue
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class CategoryNameMappingSerializer(serializers.ModelSerializer):
    CategoryName = serializers.CharField(source='CategoryCode.CategoryName', read_only=True)
    CatalogueName = serializers.CharField(source='CategoryCode.CatalogueCode.CatalogueName', read_only=True)
    CatalogueCode = serializers.CharField(source='CategoryCode.CatalogueCode', read_only=True)

    class Meta:
        model = CategoryNameMapping
        fields = ('id', 'VendorCode', 'CatalogueCode', 'CatalogueName', 'CategoryCode', 'CategoryName',
                  'CategoryName', 'is_active', "DateInserted", "DateUpdated")


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


# class ProductSerializerCarrefour(serializers.ModelSerializer):

#     class Meta:
#         model = Product_carrefour
#         fields = '__all__'
        

# class ProductSerializerAmazon(serializers.ModelSerializer):

#     class Meta:
#         model = Product_amazon
#         fields = '__all__'


# class ProductSerializerJumbo(serializers.ModelSerializer):

#     class Meta:
#         model = Product_jumbo
#         fields = '__all__'


# class ProductSerializerFirstCry(serializers.ModelSerializer):

#     class Meta:
#         model = Product_firstcry
#         fields = '__all__'



# class ProductSerializerHandM(serializers.ModelSerializer):

#     class Meta:
#         model = Product_HandM
#         fields = '__all__'


# class ProductSerializerBoots(serializers.ModelSerializer):

#     class Meta:
#         model = Product_Boots
#         fields = '__all__'



# class ProductSerializerCentrePoint(serializers.ModelSerializer):

#     class Meta:
#         model = Product_CentrePoint
#         fields = '__all__'


# class ProductSerializerMax(serializers.ModelSerializer):

#     class Meta:
#         model = Product_Max
#         fields = '__all__'


# class ProductSerializerEmax(serializers.ModelSerializer):

#     class Meta:
#         model = Product_Emax
#         fields = '__all__'


# class ProductSerializerNamshi(serializers.ModelSerializer):

#     class Meta:
#         model = Product_Namshi
#         fields = '__all__'


# class ProductSerializerLifePharmacy(serializers.ModelSerializer):

#     class Meta:
#         model = Product_LifePharmacy
#         fields = '__all__'


# class ProductSerializerAsterPharmacy(serializers.ModelSerializer):

#     class Meta:
#         model = Product_AsterPharmacy
#         fields = '__all__'


# class ProductSerializerSharafDG(serializers.ModelSerializer):

#     class Meta:
#         model = Product_SharafDG
#         fields = '__all__'


# class ProductSerializerSkechers(serializers.ModelSerializer):

#     class Meta:
#         model = Product_Skechers
#         fields = '__all__'


# class ProductSerializerAdidas(serializers.ModelSerializer):

#     class Meta:
#         model = Product_Adidas
#         fields = '__all__'


# class ProductSerializerPullBear(serializers.ModelSerializer):

#     class Meta:
#         model = Product_PullBear
#         fields = '__all__'

# class ProductSerializerSunAndSandSports(serializers.ModelSerializer):
#     class Meta:
#         model = Product_SunAndSandSports
#         fields = '__all__'

class StockAvailabilitySerializer(serializers.ModelSerializer):
    StockAvailability = serializers.CharField()
    URL = serializers.CharField()

    class Meta:
        fields = ('StockAvailability', 'URL')


class VendorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendor
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = '__all__'


class AdditionalPropertiesSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdditionalProperty
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
   # CommentDate = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f%z')
    class Meta:
        model = Review
        fields = '__all__'


# class RatingSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Rating
#         fields = '__all__'

