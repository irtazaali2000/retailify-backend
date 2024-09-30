from django.db import models
import uuid
from django.utils import timezone

class BaseModel(models.Model):
    """Provide default fields that are expected to be needed by almost all models"""
    DateInserted = models.DateTimeField(auto_now_add=True, null=True)
    DateUpdated = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True, null=True)

    class Meta:
        abstract = True


class Vendor(BaseModel):
    VendorCode = models.AutoField(primary_key=True)
    VendorName = models.CharField(max_length=250, db_index=True)  # Add index

    def __str__(self):
        return str(self.VendorCode)


class Catalogue(models.Model):
    CatalogueCode = models.AutoField(primary_key=True)
    CatalogueName = models.CharField(max_length=250, db_index=True)  # Add index

    def __str__(self):
        return str(self.CatalogueCode)


class Category(models.Model):
    CategoryCode = models.AutoField(primary_key=True)
    CategoryName = models.CharField(max_length=250, db_index=True)  # Add index
    CatalogueCode = models.ForeignKey(Catalogue, on_delete=models.CASCADE, null=True, db_index=True)  # Add index

    def __str__(self):
        return str(self.CategoryCode)


class CategoryNameMapping(BaseModel):
    VendorCode = models.ForeignKey(Vendor, on_delete=models.CASCADE, db_index=True)  # Add index
    CategoryCode = models.ForeignKey(Category, on_delete=models.CASCADE, db_index=True)  # Add index
    CategoryName = models.TextField()

    def __str__(self):
        return str(self.id)


class Product(BaseModel):
    ProductCode = models.AutoField(primary_key=True)
    CatalogueCode = models.ForeignKey(Catalogue, on_delete=models.CASCADE, null=True, db_index=True)  # Add index
    CategoryCode = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, db_index=True)  # Add index
    VendorCode = models.ForeignKey(Vendor, on_delete=models.CASCADE, db_index=True)  # Add index
    SKU = models.CharField(max_length=250, unique=True, db_index=True)  # Add index
    ProductName = models.TextField(blank=True, db_index=True)  # Add index
    URL = models.TextField(blank=True)
    MainImage = models.TextField(max_length=500, blank=True, null=True)
    CatalogueName = models.CharField(max_length=250)
    CategoryName = models.CharField(max_length=250)
    BrandCode = models.CharField(max_length=255, null=True, blank=True, db_index=True)  # Add index
    BrandName = models.CharField(max_length=255, blank=True)
    Currency = models.CharField(max_length=100)
    Market = models.CharField(max_length=100)
    About = models.TextField(blank=True, null=True, default='')
    StockAvailability = models.BooleanField(default=True)
    Offer = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=19)
    RegularPrice = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=19)
    ModelName = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    ModelNumber = models.CharField(max_length=255, blank=True, null=True, default='', db_index=True)  # Add index
    RatingValue = models.DecimalField(default=0, decimal_places=2, max_digits=19)

    def __str__(self):
        return str(self.ProductCode)

    class Meta:
        indexes = [
            models.Index(fields=['SKU', 'CategoryCode', 'VendorCode']),  # Composite index
            models.Index(fields=['ProductName']),  # Index for product name search
        ]


class AdditionalProperty(models.Model):
    ProductCode = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)  # Add index
    SKU = models.CharField(max_length=255, db_index=True)  # Add index
    AdditionalProperty = models.TextField()

    def __str__(self):
        return str(self.ProductCode.ProductCode)


class Image(models.Model):
    ProductCode = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)  # Add index
    SKU = models.CharField(max_length=255, db_index=True)  # Add index
    image_url = models.TextField(blank=True)

    def __str__(self):
        return str(self.ProductCode.ProductCode)


class Review(models.Model):
    ProductCode = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)  # Add index
    SKU = models.CharField(max_length=255, db_index=True)  # Add index
    Comment = models.TextField()
    Source = models.CharField(blank=True, max_length=255)
    CommentDate = models.DateField()
    rating = models.DecimalField(default=0, decimal_places=2, max_digits=19)
    max_rating = models.DecimalField(default=0, decimal_places=2, max_digits=19)
    average_rating = models.DecimalField(default=0, decimal_places=2, max_digits=19)

    def __str__(self):
        return str(self.ProductCode.ProductCode)


class OurStoreProduct(BaseModel):
    ProductCode = models.AutoField(primary_key=True)
    ProductName = models.CharField(max_length=250, db_index=True)  # Add index
    SKU = models.CharField(max_length=250, unique=True, db_index=True)  # Add index
    URL = models.TextField(blank=True, null=True)
    MainImage = models.TextField(max_length=500, blank=True, null=True)
    BrandName = models.CharField(max_length=255, blank=True, db_index=True)  # Add index
    Currency = models.CharField(max_length=100)
    Market = models.CharField(max_length=100)
    About = models.TextField(blank=True, null=True, default='')
    StockAvailability = models.BooleanField(default=True)
    Cost = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=19)
    MyPrice = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=19)
    ModelName = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    ModelNumber = models.CharField(max_length=255, null=True, default='', db_index=True)  # Add index
    RatingValue = models.DecimalField(default=0, decimal_places=2, max_digits=19)
    CatalogueCode = models.ForeignKey(Catalogue, on_delete=models.CASCADE, null=True, db_index=True)  # Add index
    CatalogueName = models.CharField(max_length=255, db_index=True)  # Add index
    CategoryCode = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, db_index=True)  # Add index
    CategoryName = models.CharField(max_length=255, db_index=True)   # Add index

    def __str__(self):
        return str(self.ProductCode)

    class Meta:
        indexes = [
            models.Index(fields=['SKU', 'CategoryCode', 'BrandName']),  # Composite index
        ]


class ProductAttribute(models.Model):
    """
    Model to store key-value pairs for dynamic product attributes
    """
    ProductCode = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)  # Add index
    AttributeName = models.CharField(max_length=255, db_index=True)  # Add index
    AttributeValue = models.CharField(max_length=255, db_index=True)  # Add index

    def __str__(self):
        return f"{self.ProductCode.ProductCode} - {self.AttributeName}"


class OurStoreProductAttribute(models.Model):
    """
    Model to store key-value pairs for dynamic attributes in OurStoreProduct
    """
    ProductCode = models.ForeignKey(OurStoreProduct, on_delete=models.CASCADE, db_index=True)  # Add index
    AttributeName = models.CharField(max_length=255, db_index=True)  # Add index
    AttributeValue = models.CharField(max_length=255, db_index=True)  # Add index

    def __str__(self):
        return f"{self.ProductCode.ProductCode} - {self.AttributeName}"

