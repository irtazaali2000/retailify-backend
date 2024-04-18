import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime
from ..items import ProductItemCarrefour
from ..settings import HOST, CATALOGUE_URL_T
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import mysql.connector



class CarreFourSpider(Spider):
    name = 'carrefour'
    allowed_domains = ['carrefouruae.com']
    main_url = 'https://www.carrefouruae.com'
    products_api = 'https://www.carrefouruae.com/api/v8/categories/{}?filter=&sortBy=relevance&currentPage={}&pageSize=60&maxPrice=&minPrice=&areaCode=DubaiFestivalCity-Dubai&lang=en&displayCurr=AED&latitude=25.2171003&longitude=55.3613635&needVariantsData=true&nextOffset=&needVariantsData=true&requireSponsProducts=true&responseWithCatTree=true&depth=3'

    headers = {
        'Content-Type': 'application/json',
        'Storeid': 'mafuae'
    }
    custom_settings = {
       # 'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100,
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',  #
    }

    page = 0

    categories = {
        "Fresh Food": "F1600000",
        "Fruits and Vegetables": "F11600000",
        "Food Cupboard": "F1700000",
        "Beverages": "F1500000",
        "Frozen Food": "F6000000",
        "Bakery": "F1610000",
        "Bio and Organic Food": "F1200000",
        "Cleaning and Household": "NF3000000",
        "Beauty and Personal Care": "NF2000000",
        "Baby Products": "F1000000",
        "Electronics and Appliances": "NF4000000",
        "Smartphones, Tablets and Wearables": "NF1200000",
        "Home and Garden": "NF8000000",
        "Pet Supplies": "F1100000",
        "Health and Fitness": "NF7000000",
        "Stationery and School Supplies": "NF1300000",
        "Fashion, Accessories and Luggage": "NF5000000"
    }


    conn = mysql.connector.connect(
            # host='localhost',
            # user='root',
            # password='admin',
            # database='gb'
            host="mysqldb.cb2aesoymr8i.eu-west-2.rds.amazonaws.com",
            user="datapillar",
            password="4wIwdBmMSJ3BLBVCesJT",
            database="scrappers_db",
            port="3306"
        )
    cursor = conn.cursor()

    def __init__(self, reviews='False', short_scraper="False", *args, **kwargs):
        super().__init__()

        self.reviews = reviews.lower() == 'true'
        self.short_scraper = short_scraper.lower() == 'true'
        catalogue_url = CATALOGUE_URL_T.format(self.name, self.short_scraper)
        categories_url = "{}{}".format(HOST, catalogue_url)
        raw_res = requests.get(categories_url).json()
    #     self.categories = raw_res.get('data', [])
        self.vendor_code = raw_res.get('VendorCode')

    def get_catalogue_code(self, catalogue_name):
        # Attempt to retrieve the catalogue code from the database
        query = "SELECT CatalogueCode FROM product_catalogue WHERE CatalogueName = %s"
        self.cursor.execute(query, (catalogue_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the catalogue code exists, return it
            return result[0]
        else:
            # If the catalogue code doesn't exist, insert it into the database
            insert_query = "INSERT INTO product_catalogue (CatalogueName) VALUES (%s)"
            self.cursor.execute(insert_query, (catalogue_name,))
            self.conn.commit()  # Commit the transaction
            
            # Retrieve the newly inserted catalogue code
            self.cursor.execute(query, (catalogue_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
    
    def get_category_code(self, category_name, catalogue_code):
        # Attempt to retrieve the category code from the database
        query = "SELECT CategoryCode FROM product_category WHERE CategoryName = %s"
        self.cursor.execute(query, (category_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the category code exists, return it
            return result[0]
        else:
            # If the category code doesn't exist, insert it into the database
            insert_query = "INSERT INTO product_category (CategoryName, CatalogueCode_id) VALUES (%s, %s)"
            self.cursor.execute(insert_query, (category_name, catalogue_code))
            self.conn.commit()  # Commit the transaction
            
            # Retrieve the newly inserted category code
            self.cursor.execute(query, (category_name,))
            result = self.cursor.fetchone()
            # print("*******************")
            # print(result[0])
            return result[0] if result else None
        
    def start_requests(self):
        for category, category_code in self.categories.items():
            catalogue_code = self.get_catalogue_code(category)
            if catalogue_code:
                yield scrapy.Request(url=self.products_api.format(category_code, self.page), headers=self.headers,
                                    meta={'category': category, 'category_code': category_code, 'page': self.page, 'catalogue_code': catalogue_code})
            

    def parse(self, response):
        item = ProductItemCarrefour()
        item['CatalogueName'] = response.meta['category']
        category_code = response.meta['category_code']
        page = response.meta['page']
        vendor_code = self.vendor_code
        data = json.loads(response.text)
        products = data.get('data', {}).get('products', [])
        if products:
            for product in products:
                item['SKU'] = product.get('id')
                item['ProductName'] = product.get('name')

                item['BrandName'] = product.get('brand', {}).get('name')
                if not item['BrandName']:
                    item['BrandName'] = ''

                item['BrandCode'] = product.get('brand', {}).get('id')
                if not item['BrandCode']:
                    item['BrandCode'] = ''

                item['StockAvailability'] = product.get('availability', {}).get('isAvailable')
                item['RegularPrice'] = product.get('price', {}).get('price')
                item['RegularPrice'] = round(float(item['RegularPrice']), 2)
                item['Offer'] = product.get('price', {}).get('discount', {}).get('price')
                item['Offer'] = round(float(item['Offer']), 2)
                sub_category = product.get('productCategoriesHearchi')
                item['CategoryName'] = sub_category.split("/")[-1]
                item['MainImage'] = product.get('links', {}).get('images', [])
                if item['MainImage']:
                    item['MainImage'] = item['MainImage'][0].get('href')

                item['URL'] = product.get('links', {}).get('productUrl', {}).get('href')
                item['VendorCode'] = vendor_code
                item['RatingValue'] = 0
                item['ModelNumber'] = ''
                catalogue_code = response.meta['catalogue_code']
                category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                item['CatalogueCode'] = catalogue_code
                item['CategoryCode'] = category_code

                yield item

            
            #NEXT PAGE
            page = page + 1
            yield scrapy.Request(url=self.products_api.format(category_code, page), headers=self.headers,
                                 meta={'category': item['CatalogueName'], 'category_code': category_code, 'page': page, 'catalogue_code': catalogue_code})
            
