# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FirstcryItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    ProductName = scrapy.Field()
    ProductDesc = scrapy.Field()
    MainImage = scrapy.Field()
    images = scrapy.Field()
    URL = scrapy.Field()
    SKU = scrapy.Field()
    BrandName = scrapy.Field()
    AdditionalProperty = scrapy.Field()
    ModelName = scrapy.Field()
    ModelNumber = scrapy.Field()
    StockAvailability = scrapy.Field()
    RegularPrice = scrapy.Field()
    Offer = scrapy.Field()
    reviews = scrapy.Field()
    Rating = scrapy.Field()
    RatingValue = scrapy.Field()
    BestRating = scrapy.Field()
    ReviewCount = scrapy.Field()

    pass


class ProductItem(scrapy.Item):
    ProductId = scrapy.Field()
    ProductName = scrapy.Field()
    RegularPrice = scrapy.Field()
    StockAvailability = scrapy.Field()
    url = scrapy.Field()
    MainImage = scrapy.Field()
    CategoryName = scrapy.Field()
    BrandName = scrapy.Field()


class ProductItemAmazon(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()


class ProductItemJumbo(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()
    #page = scrapy.Field()

    
class ProductItemFirstCry(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()


class ProductItemHandM(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    #ProductDesc = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()


class ProductItemBoots(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()



class ProductItemCentrePoint(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()


class ProductItemMax(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()



class ProductItemEmax(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()



class ProductItemNamshi(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    #ProductDesc = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    #SubBrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    #ModelName = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    #BestRating = scrapy.Field()
    #ReviewCount = scrapy.Field()
    VendorCode = scrapy.Field()


    # is_active = scrapy.Field()
    # DateInserted = scrapy.Field()
    # DateUpdated = scrapy.Field()



class ProductItemLifePharmacy(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()



class ProductItemAsterPharmacy(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()



class ProductItemSharafDG(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    #ProductDesc = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    #SubBrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    #ModelName = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    #BestRating = scrapy.Field()
    #ReviewCount = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()
    



class ProductItemSkechers(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()
    page = scrapy.Field()



class ProductItemAdidas(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()                         



class ProductItemPullBear(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()  



class ProductItemSunAndSandSports(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()



class ProductItemNoon(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()


class ProductItemCarrefour(scrapy.Item):
    SKU = scrapy.Field()
    ProductName = scrapy.Field()
    URL = scrapy.Field()
    MainImage = scrapy.Field()
    CatalogueName = scrapy.Field()
    CategoryName = scrapy.Field()
    CategoryCode = scrapy.Field()
    CatalogueCode = scrapy.Field()
    BrandCode = scrapy.Field()
    BrandName = scrapy.Field()
    StockAvailability = scrapy.Field()
    Offer = scrapy.Field()
    RegularPrice = scrapy.Field()
    ModelNumber = scrapy.Field()
    RatingValue = scrapy.Field()
    VendorCode = scrapy.Field()
    reviews = scrapy.Field()

                                                        
