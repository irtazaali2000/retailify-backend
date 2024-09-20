import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemEmax
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import os
import psycopg2



class EmaxSpider(Spider):
    name = 'emax'
    allowed_domains = ['uae.emaxme.com', '3hwowx4270-dsn.algolia.net']
    main_url = 'https://uae.emaxme.com'
    products_api = 'https://3hwowx4270-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.22.1)%3B%20Browser'
    headers = {'Content-Type': 'application/json', 'X-Algolia-Api-Key': '4c4f62629d66d4e9463ddb94b9217afb', 'X-Algolia-Application-Id': '3HWOWX4270'}
    body = {"requests":[{"indexName":"prod_uae_emax_product","query":"*","params":"facets=*&page={}&hitsPerPage=48&attributesToRetrieve=*&attributesToHighlight=%5B%22name%22%5D&maxValuesPerFacet=1000&getRankingInfo=true&facetFilters=%5B%22inStock%3A1%22%2C%22approvalStatus%3A1%22%2C%22allCategories%3A{}%22%5D&numericFilters=%5B%22price%20%3E%200%22%5D&clickAnalytics=true"}]}
    #Just make page and category name dynamic in body

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100,
        #'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }
    page = 0
    count = 0
    

    categories = {
                'Mobiles Tablets & Wearables': {
                                            'Mobile Phones': 'mobile',
                                            #'Mobile Accessories': 'mobileaccessories',
                                            #'Tablets & Ereaders': 'laptoptabletandcomputeraccessories-tablets'
                                            },
                
                'Computers': {
                                'Laptops': 'laptoptabletandcomputeraccessories-laptops',
                                #'Computers Accessories': 'laptoptabletandcomputeraccessories-computeraccessories'
                                
                            },

                'Video, Lcd & Oled': {
                            'Tv': 'televisionandaudio-television',
                },

                'Audio, Headphones & Music Players': {
                    #'Audio Accessories': 'televisionandaudio-audio'
                },

                # 'Home Appliances': {
                #     'Home Appliances Accessories': 'homeappliances',
                #     'Kitchen Appliances': 'kitchenappliances'
                # },

                # 'Personal Care & Beauty': {
                #     'Makeup & Accessories': 'personalcare'
                # },

                # 'Video Games & Consoles': {
                #     'Games Accessories': 'gamingandgamingaccessories'
                # },

                'Camcorders & Cameras': {
                    'Camera Accessories': 'photographylensesanddrones'
                    },

                # 'Musical Instruments': {
                #     'Keyboards & Midi Instruments': 'musicalinstruments'
                # }
                    
        }
    
    conn = psycopg2.connect(
        dbname="retailifydb",
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
        for main_category, subcategories in self.categories.items():
            catalogue_code = self.get_catalogue_code(main_category)
            if catalogue_code:
                for sub_category, sub_category_code in subcategories.items():
                    modified_body = copy.deepcopy(self.body)
                    format_body = modified_body["requests"][0]["params"].format(self.page, sub_category_code)
                    modified_body["requests"][0]["params"] = format_body
                    body = json.dumps(modified_body)
                    
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers,
                                        body=body, callback=self.parse,
                                        meta={'category': main_category, 'sub_category': sub_category, 'category_code_f': sub_category_code, 'page': self.page, 'vendor_code': self.vendor_code, 'catalogue_code': catalogue_code})

        
    
    def parse(self, response):
        item = ProductItemEmax()
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        category_code_f = response.meta['category_code_f']
        vendor_code = response.meta['vendor_code']
        print("Category: ", category)
        page = response.meta['page']
        data = json.loads(response.text)
        results = data.get('results', [])
        for result in results:
            hits = result.get('hits', [])
            if hits:
                #self.count = 0
                for hit in hits:
                    item['ProductName'] = hit.get('name', {}).get('en')
                    #manufacturer_name = hit.get('manufacturerName', '')
                    #if isinstance(manufacturer_name, str):
                     #   item['manufacturer_name'] = manufacturer_name
                    #else:
                     #   item['manufacturer_name'] = ''
                    
                    item['StockAvailability'] = hit.get('inStock')
                    item['BrandName'] = hit.get('brand', '')
                    item['BrandCode'] = hit.get('brandId', '')
                    #item['product_id'] = hit.get('productId')
                    item['SKU'] = hit.get('sku')
                    item['Offer'] = hit.get('price')
                    item['Offer'] = round(float(item['Offer']), 2)
                    item['RegularPrice'] = hit.get('wasPrice', 0)
                    item['RegularPrice'] = round(float(item['RegularPrice']), 2)

                    if item['RegularPrice'] == item['Offer']:
                        item['Offer'] = 0

                    # item['MyPrice'] = hit.get('price')
                    # item['MyPrice'] = round(float(item['MyPrice']), 2)
                    # item['Cost'] = hit.get('wasPrice', 0)
                    # item['Cost'] = round(float(item['Cost']), 2)

                    # if item['Cost'] == item['MyPrice']:
                    #     item['MyPrice'] = 0

                    img = hit.get('galleryImages', [])
                    if img:
                        item['MainImage'] = img[0].get('url', '')
                    else:
                        item['MainImage'] = ''
                    #item['color'] = hit.get('color', '')
                    #item['description'] = hit.get('description', {}).get('en', '')
                    url = hit.get('uri')
                    url = url.strip()
                    url = url.replace(" ", "%20")
                    item['URL'] = self.main_url + url
                    #item['percentage_discount'] = hit.get('percentageDiscount', 0)
                    item['CatalogueName'] = category
                    #item['CategoryName'] = hit.get('allCategories', [])[-1]
                    item['CategoryName'] = sub_category
                    #item['page'] = page
                    item['RatingValue'] = 0
                    item['ModelNumber'] = ''
                    item['Currency'] = 'AED'
                    item['About'] = hit.get('description', {}).get('en')
                    item['VendorCode'] = vendor_code
                    catalogue_code = response.meta['catalogue_code']
                    category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                    item['CatalogueCode']= catalogue_code
                    item['CategoryCode']= category_code

                    self.count+=1
                    yield item
                
                print("Category = {}, Total Products = {} on Page = {}".format(category, self.count, page))
                #Next Page

                page = page + 1
                modified_body = copy.deepcopy(self.body)      
                format_body = modified_body["requests"][0]["params"].format(page, category_code_f)
                modified_body["requests"][0]["params"] = format_body
                body = json.dumps(modified_body)
                #print(body)
                yield scrapy.Request(url=self.products_api, method='POST', callback=self.parse, headers=self.headers, body=body, meta={'category':category, 'sub_category': sub_category, 'category_code_f': category_code_f, 'page': page, 'vendor_code': vendor_code, 'catalogue_code': catalogue_code})

