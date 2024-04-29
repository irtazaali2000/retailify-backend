import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemNamshi
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import mysql.connector




class NamshiSpider(Spider):
    name = 'namshi'
    allowed_domains = ['namshi.com']
    main_img_url = 'https://www.namshi.com/uae-en'
    products_api = 'https://www.namshi.com/_svc/catalog/products'
    headers = {'Content-Type': 'application/json'}
    body = {"uri":"/{}/?page={}"}
    #Just make page and category name dynamic in body

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 200,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,  # Number of retries for each request
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 400, 408]  # HTTP status codes to retry
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }
    page = 0
    count = 0

    conn = mysql.connector.connect(
            # host='localhost',
            # user='root',
            # password='admin',
            # database='gb',

            host='mysqldb.cb2aesoymr8i.eu-west-2.rds.amazonaws.com',
            user='datapillar',
            password='4wIwdBmMSJ3BLBVCesJT',
            database='scrappers_db'
        )
    cursor = conn.cursor()
    
    
    categories_l = {
                "Fashion": {
                    'Women Clothing': 'women-clothing', 
                    'Women Shoes': 'women-shoes', 
                    'Women Accessories': 'women-accessories', 
                    'Women Bags': 'women-bags',  
                    'Women Accessories': 'women-lifestyle',
                    "Men Shoes": 'men-shoes',
                    "Men Clothing": 'men-clothing',
                    "Men Accessories": 'men-accessories',
                    "Men Bags": 'men-bags',
                    "Men Accessories": 'men-lifestyle'

                },

                "Baby & Kids": {
                    "Boys Shoes": 'kids-shoes-boys', 
                    "Boys Clothing": 'kids-clothing-boys', 
                    "Boys Accessories": 'kids-accessories-boys', 
                    "Boys Accessories": 'kids-bags-boys', 
                    "Girls Accessories": 'kids-beauty-products', 
                    "Boys Accessories": 'kids-lifestyle-boys', 
                    "Toys": 'kids-toys-boys',
                    "Girls Shoes": 'kids-shoes-girls', 
                    "Girls Clothing": 'kids-clothing-girls', 
                    "Girls Accessories": 'kids-accessories-girls', 
                    "Girls Accessories": 'kids-bags-girls', 
                    "Girls Accessories": 'kids-lifestyle-girls', 
                    "Toys": 'kids-toys-girls'
                    },

                "Personal Care & Beauty": {
                    'Personal Care For Women': 'women-beauty-products',
                    'Personal Care For Men': 'men-beauty-products',
                }

                }



    def __init__(self, reviews='False', short_scraper="False", *args, **kwargs):
        super().__init__()

        self.reviews = reviews.lower() == 'true'
        self.short_scraper = short_scraper.lower() == 'true'
        catalogue_url = CATALOGUE_URL_T.format(self.name, self.short_scraper)
        categories_url = "{}{}".format(HOST, catalogue_url)
        raw_res = requests.get(categories_url).json()
    #     self.categories = raw_res.get('data', [])
        self.vendor_code = raw_res.get('VendorCode')
    #     print(self.vendor_code)
    #     print("############################")
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
        for main_category, sub_categories in self.categories_l.items():
            catalogue_code = self.get_catalogue_code(main_category)
            if catalogue_code:
                for sub_category, sub_category_code in sub_categories.items():
                    modified_body = copy.deepcopy(self.body)
                    format_body = modified_body["uri"].format(sub_category_code, self.page)
                    modified_body["uri"] = format_body
                    formatted_body = json.dumps(modified_body)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=formatted_body, callback=self.parse, meta={'category': main_category, 'sub_category': sub_category, 'sub_category_code': sub_category_code, 'page': self.page, 'catalogue_code': catalogue_code})

        

    def parse(self, response):
        item = ProductItemNamshi()
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        sub_category_code = response.meta['sub_category_code']
        page = response.meta['page']
        data = json.loads(response.text)
        products = data.get('products', [])

        if products:
            for product in products:
                catalogue_code = response.meta['catalogue_code']
                category_code = self.get_category_code(sub_category, catalogue_code)
                item['ProductName'] = product.get('title')
                item['SKU'] = product.get('sku')
                item['BrandName'] = product.get('brand', '')
                item['RegularPrice'] = product.get('normalPrice', 0)
                item['RegularPrice'] = round(float(item['RegularPrice']), 2)
                item['Offer'] = product.get('salePrice', 0)
                item['Offer'] = round(float(item['Offer']), 2)
                url = product.get('uri')
                item['URL'] = response.urljoin(url)
                img = product.get('imageKeys')[0]
                item['MainImage'] = self.main_img_url + img
                #item['percentage_discount'] = product.get('discountPercent', 0)
                #item['max_quantity'] = product.get('maxQty')
                #item['stock_info'] = product.get("stockInfo", {}).get("label", '')
                item['CategoryName'] = sub_category
                item['VendorCode'] = self.vendor_code
                item['CatalogueName'] = category
                item['CatalogueCode'] = catalogue_code
                item['CategoryCode'] = category_code
                item['StockAvailability'] = True
                item['BrandCode'] = product.get('brandCode', '')
                #item['SubBrandName'] = ''
                #item['ModelName'] = ''
                item['ModelNumber'] = ''
                #item['ProductDesc'] = ''
                #item['is_active'] = True

                #item['sub_category'] = sub_category
                #item['page'] = page
                self.count+=1
                yield item
            
            print("Category = {}, Sub Category = {}, Total Products = {} On Page = {}".format(category, sub_category, self.count, page))
            #Next Page
            page = page + 1
            modified_body = copy.deepcopy(self.body)
            format_body = modified_body["uri"].format(sub_category_code, page)
            modified_body["uri"] = format_body
            formatted_body = json.dumps(modified_body)
            yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=formatted_body, meta={'category': category, 'sub_category': sub_category, 'sub_category_code': sub_category_code, 'page': page, 'catalogue_code': catalogue_code})


