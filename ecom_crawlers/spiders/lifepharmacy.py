import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemLifePharmacy
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import mysql.connector



class LifePharmacySpider(Spider):
    name = 'lifepharmacy'
    allowed_domains = ['lifepharmacy.com']
    main_url = 'https://www.lifepharmacy.com/'
    products_api = 'https://prodapp.lifepharmacy.com/api/web/products?categories={}&skip={}&take=40&lang=ae-en'
    headers = {'Content-Type': 'application/json'}
    

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 200,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    page = 0
    skip = 0
    count = 0

    categories = {
        'Personal Care & Beauty': {
            'Makeup & Accessories': 'beauty-care'
        },

        'Sports Equipment': {
            'Sports Supplements': 'sports-nutrition',
        },

        
        'Health & Medical': {
            'Nutrition': 'nutrition-supplements',
        },
        
        'Home Appliances': {
            'Home Appliances Accessories': 'home-healthcare',
        },
        
        'Baby & Kids': {
            'Feeding & Nursing': 'mother-baby-care',
        },
        
        'Personal Care & Beauty': {
            'Makeup & Accessories': 'personal-care',
        },

        'Health & Medical': {
            'Medicine': 'medicines'
        }
            }
    
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
    cursor = conn.cursor(buffered=True)

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
        # Attempt to retrieve the catalog code and name from the database
        query_select = "SELECT CatalogueCode, CatalogueName FROM product_catalogue WHERE CatalogueName = %s"
        self.cursor.execute(query_select, (catalogue_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the catalog code exists, check if the name needs to be updated
            if result[1] != catalogue_name:
                update_query = "UPDATE product_catalogue SET CatalogueName = %s WHERE CatalogueCode = %s"
                self.cursor.execute(update_query, (catalogue_name, result[0]))
                self.conn.commit()  # Commit the transaction
                
            return result[0]
        else:
            # If the catalog code doesn't exist, insert it into the database
            insert_query = "INSERT INTO product_catalogue (CatalogueName) VALUES (%s)"
            self.cursor.execute(insert_query, (catalogue_name,))
            self.conn.commit()  # Commit the transaction
            
            # Retrieve the newly inserted catalog code and name
            self.cursor.execute(query_select, (catalogue_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None


    
    def get_category_code(self, category_name, catalogue_code):
        # Attempt to retrieve the category code and name from the database
        query_select = "SELECT CategoryCode, CategoryName FROM product_category WHERE CategoryName = %s"
        self.cursor.execute(query_select, (category_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the category code exists, check if the name needs to be updated
            if result[1] != category_name:
                update_query = "UPDATE product_category SET CategoryName = %s WHERE CategoryCode = %s"
                self.cursor.execute(update_query, (category_name, result[0]))
                self.conn.commit()  # Commit the transaction
            
            return result[0]
        else:
            # If the category code doesn't exist, insert it into the database
            insert_query = "INSERT INTO product_category (CategoryName, CatalogueCode_id) VALUES (%s, %s)"
            self.cursor.execute(insert_query, (category_name, catalogue_code))
            self.conn.commit()  # Commit the transaction
            
            # Retrieve the newly inserted category code and name
            self.cursor.execute(query_select, (category_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None

    
    def start_requests(self):
        for main_category, sub_categories in self.categories.items():
            for sub_category, category_f in sub_categories.items():
                catalogue_code = self.get_catalogue_code(main_category)
                if catalogue_code:
                    formatted_products_api = self.products_api.format(category_f, self.skip)
                    yield scrapy.Request(url=formatted_products_api, headers=self.headers, callback=self.parse, meta={'category': main_category, 'sub_category': sub_category, 'category_f': category_f, 'skip': self.skip, 'page': self.page, 'catalogue_code': catalogue_code})

    
    def parse(self, response):
        item = ProductItemLifePharmacy()
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        category_f = response.meta['category_f']
        skip = response.meta['skip']
        page = response.meta['page']
        data = json.loads(response.text)
        data_key = data.get('data', {})
        products = data_key.get('products', [])
        if products:
            for product in products:
                item['ProductName'] = product.get('title')
                item['SKU'] = product.get('sku')
                #item['active'] = product.get('active', True)
                brand = product.get('brand', {})
                if brand:
                    item['BrandName'] = brand.get('name', '')
                    item['BrandCode'] = brand.get('id', '')
                else:
                    item['BrandName'] = ''
                    item['BrandCode'] = ''
                #item['description'] = product.get('short_description', '')
                item['MainImage'] = product.get('images', {}).get('featured_image')
                search_offer = product.get('search_offer', {})
                if search_offer:
                    item['Offer'] = search_offer.get('prices', [])[0].get('price', {}).get('offer_price', 0)
                    item['Offer'] = round(float(item['Offer']), 2)
                    item['RegularPrice'] = search_offer.get('prices', [])[0].get('price', {}).get('regular_price', 0)
                    item['RegularPrice'] = round(float(item['RegularPrice']), 2)
                else:
                     item['Offer'] = product.get('prices', [])[0].get('price', {}).get('offer_price', 0)
                     item['Offer'] = round(float(item['Offer']), 2)
                     item['RegularPrice'] = product.get('prices', [])[0].get('price', {}).get('regular_price', 0)
                     item['RegularPrice'] = round(float(item['RegularPrice']), 2)
                #max_salable_qty = product.get('max_salable_qty', 0)
                #if not max_salable_qty:
                #    item['max_salable_qty'] = 0
                #else:
                    #item['max_salable_qty'] = max_salable_qty
                out_of_stock = product.get('out_of_stock', False)
                if out_of_stock == False:
                    out_of_stock = True
                if out_of_stock == True:
                    out_of_stock = False

                item['StockAvailability'] = out_of_stock
                # tax_rate = product.get('tax_rate', '')
                # if tax_rate:
                #     item['tax_rate'] = tax_rate
                # else:
                #     item['tax_rate'] = ''
                item['RatingValue'] = product.get('rating', 0)
                item['RatingValue'] = round(float(item['RatingValue']), 2)
                url = product.get('product_url')
                item['URL'] = self.main_url + url
                #item['CategoryName'] = product.get('categories', [])[0].get('name', '')
                item['CatalogueName'] = category
                item['CategoryName'] = sub_category
                #item['page'] = page
                item['ModelNumber'] = ''
                item['VendorCode'] = self.vendor_code
                catalogue_code = response.meta['catalogue_code']
                category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                item['CatalogueCode']= catalogue_code
                item['CategoryCode']= category_code
                self.count+=1

                yield item


            print("Category = {}, Sub Category = {}, Total Products = {} On Page = {}".format(category, item['CategoryName'], self.count, page))
            #NEXT PAGE
            skip = skip + 40
            page = page + 1
            formatted_products_api = self.products_api.format(category_f, skip)
            yield scrapy.Request(url=formatted_products_api, headers=self.headers, meta={'category': category, 'sub_category': sub_category, 'category_f': category_f, 'skip': skip, 'page': page, 'catalogue_code': catalogue_code})

