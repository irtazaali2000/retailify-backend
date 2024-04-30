from django.db import models
import uuid
from django.utils import timezone

class BaseModel(models.Model):
    """Provide default fields that are expectedly to be needed by almost all models"""
    DateInserted = models.DateTimeField(auto_now_add=True, null=True)
    DateUpdated = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True, null=True)

    class Meta:
        abstract = True


class Vendor(BaseModel):
    VendorCode = models.AutoField(primary_key=True)
    VendorName = models.CharField(max_length=250)


    def __str__(self):
        return str(self.VendorCode)


class Catalogue(models.Model):
    CatalogueCode = models.AutoField(primary_key=True)
    CatalogueName = models.CharField(max_length=250)


    def __str__(self):
        return str(self.CatalogueCode)


class Category(models.Model):
    CategoryCode = models.AutoField(primary_key=True)
    CategoryName = models.CharField(max_length=250)
    CatalogueCode = models.ForeignKey(Catalogue, on_delete=models.CASCADE, null=True)


        
    def __str__(self):
        return str(self.CategoryCode)


class CategoryNameMapping(BaseModel):
    VendorCode = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    CategoryCode = models.ForeignKey(Category, on_delete=models.CASCADE)
    CategoryName = models.TextField()


    def __str__(self):
        return str(self.id)


class Product(BaseModel):
    ProductCode = models.AutoField(primary_key=True)
    CatalogueCode = models.ForeignKey(Catalogue, on_delete=models.CASCADE, null=True)
    CategoryCode = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    VendorCode = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    SKU = models.CharField(max_length=250, unique=True)
    ProductName = models.TextField(blank=True)
    URL = models.TextField(blank=True)
    MainImage = models.TextField(blank=True)
    CatalogueName = models.CharField(max_length=250)
    CategoryName = models.CharField(max_length=250)
    BrandCode = models.CharField(max_length=255, null=True, blank=True)
    BrandName = models.CharField(max_length=255, blank=True)
    StockAvailability = models.BooleanField(default=True)
    Offer = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=19)
    RegularPrice = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=19)
    ModelNumber = models.CharField(max_length=255, null=True, blank=True)
    RatingValue = models.DecimalField(default=0, decimal_places=2, max_digits=19)

    def __str__(self):
        return str(self.ProductCode)


class AdditionalProperty(models.Model):
    ProductCode = models.ForeignKey(Product, on_delete=models.CASCADE)
    SKU = models.CharField(max_length=255)
    AdditionalProperty = models.TextField()


    def __str__(self):
        return str(self.ProductCode.ProductCode)


class Image(models.Model):
    ProductCode = models.ForeignKey(Product, on_delete=models.CASCADE)
    SKU = models.CharField(max_length=255)
    image_url = models.TextField(blank=True)


    def __str__(self):
        return str(self.ProductCode.ProductCode)


class Review(models.Model):
    ProductCode = models.ForeignKey(Product, on_delete=models.CASCADE)
    SKU = models.CharField(max_length=255)
    Comment = models.TextField()
    Source = models.CharField(blank=True, max_length=255)
    CommentDate = models.DateField()
    rating = models.DecimalField(default=0, decimal_places=2, max_digits=19)
    max_rating = models.DecimalField(default=0, decimal_places=2, max_digits=19)
    average_rating = models.DecimalField(default=0, decimal_places=2, max_digits=19)

    
    def __str__(self):
        return str(self.ProductCode.ProductCode)





















































# class Rating(models.Model):
#     ProductCode = models.ForeignKey(Product, on_delete=models.CASCADE)
#     SKU = models.CharField(max_length=255)
#     Rating1 = models.IntegerField()
#     Rating2 = models.IntegerField()
#     Rating3 = models.IntegerField()
#     Rating4 = models.IntegerField()
#     Rating5 = models.IntegerField()


    # def __str__(self):
    #     return str(self.ProductCode.ProductCode)

