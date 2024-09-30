import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemJumbo
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import psycopg2
import os
from copy import deepcopy


class JumboSpider(Spider):
    name = 'jumbo'
    allowed_domains = ['www.jumbo.ae', 'mk4u402w4m-dsn.algolia.net', 'js.testfreaks.com']
    products_api = 'https://mk4u402w4m-dsn.algolia.net/1/indexes/staging_en_products/query?x-algolia-agent=Algolia%20for%20JavaScript%20(4.11.0)%3B%20Browser%20(lite)%3B%20instantsearch.js%20(4.36.0)&x-algolia-api-key=b6eb0d98aeb4e792e05f0fe182dfbc0e&x-algolia-application-id=MK4U402W4M'
    get_pid_api = 'https://js.testfreaks.com/onpage/jumbo.ae-staging/reviews.json?key={}&score_dist=5&storeCode=en'
    #review_api = 'https://js.testfreaks.com/badge/jumbo.ae-staging/reviews.json?offset=1&pid={}&type=user&limit=1'
    #body = {"query":"","ruleContexts":["magento-category-{}"],"page":1,"facets":["*"],"hitsPerPage":24,"filters":"","facetFilters":["visibility_search:1","in_stock:1","categoryIds:{}"]}
    

    # categories = {
    #     # Mobiles Tables & Wearables
    #     "Electronics": {
    #         'Mobile Phones': 401,
    #         # "Mobile Accessories": 353,
    #         # "Wearables": 416,
    #     },

    #     #Computers
    #     'Electronics': {
    #         "Desktop": 395
    #     },
        
    #     # Video, Lcd & Oled
    #     'Electronics': {
    #         'Tv': 404
    #     },
        
    #     #Camcorders & Cameras
    #     'Electronics': {
    #         'Camera Accessories': 359
    #     },

    #     # 'Home Appliances': {
    #     #     "Home Appliances Accessories": 371
    #     # },

    #     # Audio, Headphones & Music Players
    #     'Electronics': {
    #         "Headphones & Speakers": 374
    #     },

    #     # 'Computers': {
    #     #     "Networking & Wireless": 389,
    #     # },
        
    #     # 'Video Games & Consoles': {
    #     #     "Games Accessories": 365
    #     # },
        
    #     # 'Office Supplies': {
    #     #     "Warehouse Equipment": 392,
    #     # },

    #     # 'Personal Care & Beauty': {
    #     #     "Makeup & Accessories": 377,
    #     # }
        
    #     }

    categories = {
    "Electronics": {
        'Mobile Phones': 401,
        'Desktop': 395,
        'Tv': 404,
        'Camera Accessories': 359,
        'Headphones & Speakers': 374,
    }
    }


    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100, 
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        # 'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        # 'LOG_FILE': None,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter',
    }

    count = 0
    item_reviews = []

    conn = psycopg2.connect(
        dbname="retailifydb2",
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    def __init__(self, reviews='False', short_scraper="False", *args, **kwargs):
        super().__init__()

         # Set up the log directory and file path
        log_dir = 'scrapy-logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)  # Create the directory if it doesn't exist

        log_file = f'{log_dir}/{self.name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log'
        self.custom_settings['LOG_FILE'] = log_file

        self.reviews = reviews.lower() == 'true'
        self.short_scraper = short_scraper.lower() == 'true'
        catalogue_url = CATALOGUE_URL_T.format(self.name, self.short_scraper)
        categories_url = "{}{}".format(HOST, catalogue_url)
        raw_res = requests.get(categories_url).json()
    #     self.categories = raw_res.get('data', [])
        self.vendor_code = raw_res.get('VendorCode')

    def get_catalogue_code(self, catalogue_name):
        # Attempt to retrieve the catalog code and name from the database
        query_select = 'SELECT "CatalogueCode", "CatalogueName" FROM product_catalogue WHERE "CatalogueName" = %s'
        self.cursor.execute(query_select, (catalogue_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the catalog code exists, check if the name needs to be updated
            if result[1] != catalogue_name:
                update_query = 'UPDATE product_catalogue SET "CatalogueName" = %s WHERE "CatalogueCode" = %s'
                self.cursor.execute(update_query, (catalogue_name, result[0]))
                self.conn.commit()  # Commit the transaction
                
            return result[0]
        else:
            # If the catalog code doesn't exist, insert it into the database
            insert_query = 'INSERT INTO product_catalogue ("CatalogueName") VALUES (%s) RETURNING "CatalogueCode"'
            self.cursor.execute(insert_query, (catalogue_name,))
            self.conn.commit()  # Commit the transaction

            # # Retrieve the newly inserted category code and name
            # self.cursor.execute(query_select, (catalogue_name,))
            # result = self.cursor.fetchone()
            # return result[0] if result else None
        
            result = self.cursor.fetchone()
            return result[0] if result else None


    
    def get_category_code(self, category_name, catalogue_code):
        # Attempt to retrieve the category code and name from the database
        query_select = 'SELECT "CategoryCode", "CategoryName" FROM product_category WHERE "CategoryName" = %s'
        self.cursor.execute(query_select, (category_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the category code exists, check if the name needs to be updated
            if result[1] != category_name:
                update_query = 'UPDATE product_category SET "CategoryName" = %s WHERE "CategoryCode" = %s'
                self.cursor.execute(update_query, (category_name, result[0]))
                self.conn.commit()  # Commit the transaction
            
            return result[0]
        else:
            # If the category code doesn't exist, insert it into the database
            insert_query = 'INSERT INTO product_category ("CategoryName", "CatalogueCode_id") VALUES (%s, %s) RETURNING "CategoryCode"'
            self.cursor.execute(insert_query, (category_name, catalogue_code))
            self.conn.commit()  # Commit the transaction
            
            # # Retrieve the newly inserted category code and name
            # self.cursor.execute(query_select, (category_name,))
            # result = self.cursor.fetchone()
            # return result[0] if result else None
            result = self.cursor.fetchone()
            return result[0] if result else None


    def start_requests(self):
        for main_category, sub_categories in self.categories.items():
            for sub_category, category_id in sub_categories.items():
                catalogue_code = self.get_catalogue_code(main_category)
                if catalogue_code:
                    page = 1
                    body = {
                        "query": "",
                        "ruleContexts": ["magento-category-{}".format(category_id)],
                        "page": page,
                        "facets": ["*"],
                        "hitsPerPage": 24,
                        "filters": "",
                        "facetFilters": ["visibility_search:1", "in_stock:1", "categoryIds:{}".format(category_id)],
                    }
                    yield scrapy.Request(url=self.products_api, body=json.dumps(body), method='POST', meta={'category_name': main_category, 'sub_category': sub_category, 'page': page, 'vendor_code': self.vendor_code, 'catalogue_code': catalogue_code})

    
    def parse(self, response):
        item = ProductItemJumbo()
        category_name = response.meta['category_name']
        sub_category = response.meta['sub_category']
        vendor_code = response.meta['vendor_code']
        page = response.meta['page']

        data = json.loads(response.text)
        hits = data.get('hits', [])
        if hits:
            self.count = 0
            for hit in hits:
                item['ProductName'] = hit.get('name')
                item['URL'] = hit.get('url').replace('mcprod.', '')
                item['CatalogueName'] = category_name
                #item['CategoryName'] = hit.get('categories_without_path', [])[0]
                item['CategoryName'] = sub_category
                item['MainImage'] = hit.get('image_url')
                item['StockAvailability'] = hit.get('in_stock')
                item['SKU'] = hit.get('sku')
                item['RegularPrice'] = hit.get('price', {}).get('AED', {}).get('cost_formatted')
                item['RegularPrice'] = str(item['RegularPrice']).replace('AED','').replace(',','')            
                item['RegularPrice'] = round(float(item['RegularPrice']), 2)
                item['Offer'] = hit.get('price', {}).get('AED', {}).get('default_formated')
                item['Offer'] = str(item['Offer']).replace('AED','').replace(',','')            
                item['Offer'] = round(float(item['Offer']), 2)
                if item['RegularPrice'] == item['Offer']:
                    item['Offer'] = 0
                item['BrandName'] = hit.get("Brand", '')
                # item['ModelNumber'] = hit.get('ItemNumber')
                item['VendorCode'] = vendor_code
                # item['RatingValue'] = 0
                item['BrandCode'] = ''
                item['Currency'] = 'AED'
                item['Market'] = 'UAE'
                item['About'] = hit.get('KeyProductFeatures', '')
                catalogue_code = response.meta['catalogue_code']
                category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                item['CatalogueCode']= catalogue_code
                item['CategoryCode']= category_code

                #item['page'] = page
                self.count+=1

                # yield scrapy.Request(
                #     url=self.get_pid_api.format(item['SKU']),
                #     callback=self.parse_pid,
                #     meta={'item': deepcopy(item), 'category_name': category_name, 'page': page, 'sku': item['SKU']}
                # )
        
                yield scrapy.Request(url=item['URL'], callback=self.parse_description, meta={'item': deepcopy(item)}, dont_filter=True)

            print("Total Items on Page {}: {}".format(page, self.count))
            page = page + 1
            next_body = response.request.body.replace(f'"page": {page-1}'.encode('utf-8'), f'"page": {page}'.encode('utf-8'))
            yield scrapy.Request(url=self.products_api, method='POST', body=next_body, meta={'category_name': category_name, 'sub_category': sub_category, 'page': page, 'vendor_code': self.vendor_code, 'catalogue_code': catalogue_code})


    def parse_description(self, response):
        item = response.meta['item']
        about = response.xpath('//h4[contains(text(), "Product Highlights")]/following-sibling::ul').get()
        internal_storage = response.xpath('//li[div[1][normalize-space(text())="Internal Storage"]]/div[2]/text()').get()
        color = response.xpath('normalize-space(//h4[span[@class="font-bold"][normalize-space(text())="Color"]]/text()[normalize-space() != ""])').get()
    
        item['ModelNumber'] = ''
        item['InternalStorage'] = internal_storage
        item['Color'] = color
        item['About'] = about
        yield item

    # def parse_pid(self, response):
    #     data = json.loads(response.text)
    #     item = response.meta['item']
    #     sku = response.meta['sku']

    #     # print(sku)
    #     user_review_url = data.get('user_review_url')
    #     score = data.get('score', 0)
    #     if score:
    #         item['RatingValue'] = round(float(score) / 2, 2)
    #     else:
    #         item['RatingValue'] = 0
    #     # print(user_review_url)
    #     if user_review_url:
    #         url = user_review_url + '&offset=1&limit=1'
    #         yield scrapy.Request(url=url, callback=self.parse_review, meta={'item': deepcopy(item), 'sku': sku})
    #     else:
    #         yield item


    # def parse_review(self, response):
    #     item = response.meta['item']
    #     data = json.loads(response.text)
    #     next_page_url = data.get('next_page_url')
    #     reviews = data.get('reviews', [])
    #     item_reviews = []
        
    #     if reviews:
    #         for review in reviews:
    #             comment = review.get('extract', '')
    #             source = review.get('source', '')
    #             comment_date = review.get('date', '')
    #             rating = round(float(review.get('score')) / 2, 2)
    #             max_rating = round(float(review.get('score_max')) / 2, 2)

    #             review_data = {
    #                 'Comment': comment,
    #                 'Source': source,
    #                 'CommentDate': comment_date,
    #                 'rating': rating,
    #                 'max_rating': max_rating,
    #                 'average_rating': item['RatingValue']
    #             }
    #             item_reviews.append(review_data)
            
    #         item['reviews'] = item_reviews
    #         #Next Page
    #         # if next_page_url:
    #         #     yield scrapy.Request(url=next_page_url, callback=self.parse_review, meta={'item': item})
            
    #     else:
    #         pass
    #         # # If no reviews are found, set default values for review fields
    #         # item['reviews'] = [{
    #         #     'Comment': '',
    #         #     'Source': '',
    #         #     'CommentDate': '',
    #         #     'rating': 0,
    #         #     'max_rating': 0,
    #         #     'average_rating': item['RatingValue']
    #         # }]


    #     yield item


    def parse_review(self, response):
        item = response.meta['item']
        yield item


