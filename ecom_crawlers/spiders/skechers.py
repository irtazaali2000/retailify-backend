import re
import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemSkechers
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import mysql.connector




class SkechersSpider(Spider):
    name = 'skechers'
    allowed_domains = ['skechers.com', 'edge.curalate.com']
    #main_url = 'https://www.lifepharmacy.com/'
    #products_api = 'https://edge.curalate.com/v1/media/frYaMEDnZHvkVnHh?appId=curalate&locale=en-us&noExpired=true&filter=((category:"{}"))&after={}&limit=50'
    products_api = 'https://edge.curalate.com/v1/media/frYaMEDnZHvkVnHh?&after={}&limit=50'

    headers = {
               'Content-Type': 'application/json',
            }
    
   
    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    page = 0
    after = ""
    count = 0
    
    categories = {
        'Women': {"Women Shoes": 'women'},
        'Men': {"Men Shoes": 'mens'},
        'Kids': {'Kids Shoes': 'kids'},
        'Clothing': {"Clothing and Accessories": 'clothing'},
            }
    
    conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='admin',
            database='gb'
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
        yield scrapy.Request(
            url=self.products_api.format(self.after),
            headers=self.headers,
            callback=self.parse,
            meta={'page': self.page}
        )


    def parse(self, response):
        item = ProductItemSkechers()
        vendor_code = self.vendor_code
        page = response.meta['page']
        data = json.loads(response.text)
        data_key = data.get('data', {})
        items = data_key.get('items', [])
        
        if items:
            for each_item in items:
                item['SKU'] = each_item.get('id')
                products = each_item.get('products', [])
                if products:
                    item['ProductName'] = products[0].get('name')
                    img = products[0].get('images',[])
                    if img:
                        item['MainImage'] = img[0].get('original', {}).get('link', '')
                    else:
                        item['MainImage'] = ''
                    item['RegularPrice'] = products[0].get('price', {}).get('value')
                    item['RegularPrice'] = round(float(item['RegularPrice']), 2)
                    item['Offer'] = products[0].get('price', {}).get('saleValue', 0)
                    item['Offer'] = round(float(item['Offer']), 2)
                    if not item['Offer']:
                        item['Offer'] = 0
                    item['URL'] = products[0].get('link')
                    item['StockAvailability'] = products[0].get('metadata', {}).get('isAvailable')
                    item['CatalogueName'] = products[0].get('metadata', {}).get('age_gender')
                    item['CategoryName'] = item['CatalogueName'] + "-shoes"
                    item['VendorCode'] = vendor_code
                    item['RatingValue'] = 0
                    item['BrandName'] = ''
                    item['BrandCode'] = ''
                    item['ModelNumber'] = ''
                    # catalogue_code = self.get_catalogue_code(item['CatalogueName'])
                    # category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                    # item['CatalogueCode'] = catalogue_code
                    # item['CategoryCode'] = category_code

                    item['page'] = page
                    self.count+=1
                    yield item
                    
            
            print("Category = {}, Total Products = {} on Page = {}".format(item['CatalogueName'], self.count, page))
           #Next Page
            # after = data.get('paging', {}).get('cursors', {})
            # if after:
            #     after_updated = after.get('after')
            #     page = page + 1
            #     yield scrapy.Request(url=self.products_api.format(formatted_category, after_updated), headers=self.headers, meta={'category': category, 'formatted_category': formatted_category, 'sub_category': sub_category, 'after': after_updated, 'page': page})
            next_page_url = data.get('paging', {}).get('next')
            if next_page_url:
                page = page + 1
                yield scrapy.Request(url=next_page_url, headers=self.headers, meta={'page': page})
        


        
        




