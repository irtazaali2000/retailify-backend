import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemPullBear
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import mysql.connector




class PullBearSpider(Spider):
    name = 'pullbear'
    allowed_domains = ['pullandbear.com']
    main_url = 'https://www.pullandbear.com/ae/'
    get_id_api = 'https://www.pullandbear.com/itxrest/1/search/store/25009531/query?scope=desktop&locale=en&catalogue=20309442&warehouse=102109006&section={}&sections={}&query={}&offset={}&limit=25&origin=linked&returnableFields=internal_id%2Cname%2CproductId&deviceOS=Windows&deviceType=desktop'
    products_api = 'https://www.pullandbear.com/itxrest/3/catalog/store/25009531/20309442/productsArray?languageId=-1&productIds={}&appId=1'
    headers = {'Content-Type': 'application/json'}
   
    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }
    page = 0
    offset = 0
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

    
    categories = {
                 'Fashion': {
                        "Men Clothing": 'clothing', 
                        "Men Shoes": 'shoes', 
                        "Men Accessories": 'accessories', 
                        "Men Bags": 'bags',

                        "Women Clothing": 'clothing', 
                        "Women Shoes": 'shoes', 
                        "Women Accessories": 'accessories', 
                        "Women Bags": 'bags',
                        },
                 }
    

    def start_requests(self):
        for main_category, sub_categories in self.categories.items():
            catalogue_code = self.get_catalogue_code(main_category)
            if catalogue_code:
                for sub_category, sub_category_code in sub_categories.items():
                    param = sub_category.split(' ')[0]
                    if param == "Men":
                        yield scrapy.Request(url=self.get_id_api.format("man", "Man", sub_category_code, self.offset), 
                                                meta={'category': main_category, 'sub_category': sub_category, 'sub_category_code': sub_category_code, 'catalogue_code': catalogue_code, 'offset': self.offset})

                    elif param == "Women":
                        yield scrapy.Request(url=self.get_id_api.format("woman", "Woman", sub_category_code, self.offset), 
                                                meta={'category': main_category, 'sub_category': sub_category, 'sub_category_code': sub_category_code, 'catalogue_code': catalogue_code, 'offset': self.offset})


    def parse(self, response):
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        sub_category_code = response.meta['sub_category_code']
        catalogue_code = response.meta['catalogue_code']
        offset = response.meta['offset']
        vendor_code = self.vendor_code
        data = json.loads(response.text)
        results = data.get('results', [])
        if results:
            for result in results:
                product_id = result.get('content', {}).get('productId')
                yield scrapy.Request(url=self.products_api.format(product_id), callback=self.parse_product, meta={'product_id': product_id, 'offset': offset, 'catalogue_code': catalogue_code, 'sub_category': sub_category, 'category': category, 'VendorCode': vendor_code})

            offset = offset + 25
            #if offset <= 25:
            param = sub_category.split(' ')[0]
            if param == "Men":
                yield scrapy.Request(url=self.get_id_api.format("man", "Man", sub_category_code, offset), 
                                        meta={'category': category, 'sub_category': sub_category, 'sub_category_code': sub_category_code, 'catalogue_code': catalogue_code, 'offset': offset})
            elif param == "Women":
                yield scrapy.Request(url=self.get_id_api.format("woman", "Woman", sub_category_code, offset), 
                                        meta={'category': category, 'sub_category': sub_category, 'sub_category_code': sub_category_code, 'catalogue_code': catalogue_code, 'offset': offset})
                
    def parse_product(self, response):
        item = ProductItemPullBear()
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        offset = response.meta['offset']
        vendor_code = response.meta['VendorCode']
        data = json.loads(response.text)
        products = data.get('products', [])
        if products:
            for product in products:
                item['SKU'] = product.get('id')
                item['ProductName'] = product.get('name', '')
                #item['CatalogueName'] = product.get('sectionNameEN', '')
                item['CatalogueName'] = category
                item['CategoryName'] = sub_category
                # sub_category = product.get('relatedCategories', [])
                # if sub_category:
                #     sub_category = sub_category[0].get('name', '')
                #     sub_category = sub_category + '>' + product.get('familyName', '')
                #     new_sub_category = product.get('subFamilyName', '')
                #     if new_sub_category:
                #         item['CategoryName'] = sub_category + '>' + new_sub_category
                #     else:
                #         item['CategoryName'] = sub_category
                #item['description'] = product.get('detail', {}).get('longDescription', '')
                item['Offer'] = product.get('detail', {}).get('colors', [])[0].get('sizes', [])[0].get('price', 0)
                item['Offer'] = float(item['Offer']) / 100
                item['Offer'] = round(float(item['Offer']), 2)
                item['RegularPrice'] = product.get('detail', {}).get('colors', [])[0].get('sizes', [])[0].get('oldPrice', 0)
                if item['RegularPrice']:
                    item['RegularPrice'] = float(item['RegularPrice']) / 100  
                    item['RegularPrice'] = round(float(item['RegularPrice']), 2)
                if not item['RegularPrice']:
                    item['RegularPrice'] = 0
                item['URL'] = self.main_url + product.get('productUrl', '')
                item['StockAvailability'] = product.get('isBuyable', True)
                #item['offset'] = offset
                item['BrandName'] = ''
                item['BrandCode'] = ''
                item['ModelNumber'] = ''
                item['VendorCode'] = vendor_code
                catalogue_code = response.meta['catalogue_code']
                category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                item['CatalogueCode'] = catalogue_code
                item['CategoryCode'] = category_code
                item['MainImage'] = ''


                yield item
                