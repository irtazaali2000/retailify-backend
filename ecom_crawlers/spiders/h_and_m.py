import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemHandM
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import mysql.connector




class HandMSpiderOld(Spider):
    name = 'h_and_mOld'
    allowed_domains = ['www2.hm.com']
    
    products_men_api = 'https://www2.hm.com/en_us/men/products/view-all/_jcr_content/main/productlisting_fa5b.display.json?sort=stock&image-size=small&image=model&offset={}&page-size=36'
    products_women_api = 'https://www2.hm.com/en_us/women/products/view-all/_jcr_content/main/productlisting_30ab.display.json?sort=stock&image-size=small&image=model&offset={}&page-size=36'
    products_baby_api = 'https://www2.hm.com/en_us/baby/products/view-all/_jcr_content/main/productlisting.display.json?sort=stock&image-size=small&image=stillLife&offset={}&page-size=36'
    products_kids_api = 'https://www2.hm.com/en_us/kids/products/view-all/_jcr_content/main/productlisting_acbd.display.json?sort=stock&image-size=small&image=model&offset={}&page-size=36'
    products_home_api = 'https://www2.hm.com/en_us/home/products/view-all/_jcr_content/main/productlisting_c559.display.json?sort=stock&image-size=small&image=stillLife&offset={}&page-size=36'
    products_beauty_api = 'https://www2.hm.com/en_us/beauty/shop-by-product/view-all/_jcr_content/main/productlisting.display.json?sort=stock&image-size=small&image=stillLife&offset={}&page-size=36'
    
    headers = {'Content-Type': 'application/json'}
    offset_men = 0
    offset_women = 0
    offset_baby = 0
    offset_kids = 0
    offset_home = 0
    offset_beauty = 0

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 500, 
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,  # Number of retries for each request
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 400, 408]  # HTTP status codes to retry
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    count = 0

    page = 1

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
        categories = [
            ('Men', self.products_men_api, self.offset_men),
            ('Women', self.products_women_api, self.offset_women),
            ('Baby', self.products_baby_api, self.offset_baby),
            ('Kids', self.products_kids_api, self.offset_kids),
            ('Home', self.products_home_api, self.offset_home),
            ('Beauty', self.products_beauty_api, self.offset_beauty)
        ]

        for category, api_format, offset_value in categories:
            catalogue_code = self.get_catalogue_code(category)
            if catalogue_code:
                yield scrapy.Request(
                    url=api_format.format(offset_value),
                    headers=self.headers,
                    callback=self.parse,
                    meta={'main_category': category, 'offset': offset_value, 'page': self.page, 'vendor_code': self.vendor_code, 'catalogue_code': catalogue_code}
                )



    def parse(self, response):
        item = ProductItemHandM()
        main_category = response.meta['main_category']
        vendor_code = response.meta['vendor_code']
        catalogue_code = response.meta['catalogue_code']
        offset = response.meta['offset']
        page = response.meta['page']
        next_page_url = ''
        data = json.loads(response.text)
        products = data.get('products', [])
        if products:
            for product in products:                
                item['ProductName'] = product.get('title')
                item['CatalogueName'] = main_category
                item['CategoryName'] = product.get('category')
                item['SKU'] = product.get('articleCode')
                url = product.get('link')
                item['URL'] = response.urljoin(url)
                img = product.get('image', [])[0].get('src')
                item['MainImage'] = response.urljoin(img)
                item['RegularPrice'] = product.get('price')
                item['Offer'] = product.get('redPrice', 0)
                #item['selling_attribute'] = product.get('sellingAttribute')
                item['BrandName'] = product.get('brandName')
                item['ModelNumber'] = ""
                item['RatingValue'] = 0
                item['VendorCode'] = vendor_code
                item['BrandCode'] = ''
                item['StockAvailability'] = 1
                #catalogue_code = self.get_catalogue_code(main_category)
                category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                item['CatalogueCode'] = catalogue_code
                item['CategoryCode'] = category_code

                #item['page'] = page
                self.count+=1
                yield item

            print("################################################################")
            print("Category = {}, Offset = {}, Total Products = {}".format(main_category, offset, self.count))
            #self.count = 0
            if main_category == 'Men':
                self.offset_men += 36
                offset = self.offset_men
                page += 1
                next_page_url = self.products_men_api.format(self.offset_men)

            elif main_category == 'Women':
                self.offset_women += 36
                offset = self.offset_women
                page += 1
                next_page_url = self.products_women_api.format(self.offset_women)

            if main_category == 'Baby':
                self.offset_baby += 36
                offset = self.offset_baby
                page += 1
                next_page_url = self.products_baby_api.format(self.offset_baby)
        
            if main_category == 'Kids':
                self.offset_kids += 36
                offset = self.offset_kids
                page += 1
                next_page_url = self.products_kids_api.format(self.offset_kids)

            if main_category == 'Home':
                self.offset_home += 36
                offset = self.offset_home
                page += 1
                next_page_url = self.products_home_api.format(self.offset_home)

            if main_category == 'Beauty':
                self.offset_beauty += 36
                offset = self.offset_beauty
                page += 1
                next_page_url = self.products_beauty_api.format(self.offset_beauty)

            
            #Crawl Next Page
            yield scrapy.Request(url=next_page_url, headers=self.headers, meta={'main_category': main_category, 'offset': offset, 'page': page, 'vendor_code': vendor_code, 'catalogue_code': catalogue_code})
           