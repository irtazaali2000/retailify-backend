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
        "Groceries": {
            "Fresh Food": "F1600000",
            "Fruits and Vegetables": "F11600000",
            "Food Cupboard": "F1700000",
            "Drinks": "F1500000",
            "Frozen Foods": "F6000000",
            "Milk, Butter & Eggs": "F1610000",
            "Fresh Food": "F1200000",
            "Pet Foods": "F1100000",
        },

        'Home Appliances': {
            "Home Necessities": "NF3000000",
            "Home Necessities": "NF4040300",
            'Vacuum Cleaners': 'NF4040800',
            'Climate Control': 'NF4040100',
            'Kitchen Appliances': 'NF4040600',
            'Kitchen Appliances': 'NF4040400',
            'Kitchen Appliances': 'NF4040700',
            'Sewing Machines': 'NF4040110'

        },

        'Personal Care & Beauty': {
            "Makeup & Accessories": "NF2000000",
        },

        'Baby & Kids': {
            "Diapers, Bath & Skincare": "F1000000",
            'Toys': 'NF1400000'
        },        
       
        'Video Games & Consoles': {
            "Consoles": "NF4090100",
        },

        'Computers': {
            'Laptops': 'NF4070500',
            'Desktop': 'NF4070800',
            'Hard Drives & Storage': 'NF4070300',
            'Networking & Wireless': 'NF4070700',
            'Computer Accessories': 'NF4070200',
            'Software': 'NF4071000',
            'Ink, Toners & Cartridges': 'NF4071100'
        },


        'Video, Lcd & Oled': {
            'Projectors & Screens': 'NF4080100',
            'Video & Tv Accessories': 'NF4080300',
            'Dvd, Blurays & Digital Media Players': 'NF4080700',
            'Home Theater': 'NF4050500',
            
        },

        'Office Supplies': {
            'ID Card Printer & Supplies': 'NF4070900'
        },


        'Mobiles Tablets & Wearables': {
            "Mobile Phones": "NF1200000",
            "Mobile Phones": "NF4060200",
            "Mobile Phones": 'NF4060100',
            'Mobile Phones': 'NF1220200',
            'Mobile Phones': 'NF1220100',
            'Wearables': 'NF1220300',
            'Mobile Accessories': 'NF1210000',
            'Tablets & Ereaders': 'NF1230000'

        },

        'Furniture, Home And Garden': {
            "Home Decor And Accessories": "NF8000000",
            "Home Decor And Accessories": "NF8013000",
            "Bathroom Accessories": "NF8010000",
            "Home Decor And Accessories": "NF8020000",
            "Home Decor And Accessories": 'NF8030100',
            "Home Decor And Accessories": 'NF8030200',
            "Home Decor And Accessories": 'NF8030300',
            "Home Decor And Accessories": 'NF8030500',
            "Home Decor And Accessories": 'NF8050000',
            "Home Decor And Accessories": 'NF8060000',
            "Home Decor And Accessories": 'NF8070000',
            "Home Decor And Accessories": 'NF8080000',
            "Home Decor And Accessories": 'NF8100000',
            "Home Decor And Accessories": 'NF8120000',
            'Kitchen Accessories': 'NF8090000',
            'Kitchen Accessories': 'NF8030400',
            "Outdoor": "NF8030600",
            'Pet Accessories': 'F1100000',
            'Flowers & Plants': 'NF9010000'
        },
         
         'Health & Medical': {
            "Health And Fitness": "NF7000000",
         },
       
        'Office Supplies': {
            "Stationary": "NF1300000",
            
        },
        
        'Audio, Headphones & Music Players': {
           'Headphones & Speakers': 'NF4051000',
           'Recording Equipment': 'NF4050900',
           'Music Players': 'NF4050600',
           },

        
        'Car Parts & Accessories': {
            'Car Accessories': 'NF2302000',
            'Car Audio': 'NF2301000'
        },

        'Books': {
            'Fiction Books': 'NF9030300',
            'Non-Fiction Books': 'NF9030100'
        }
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
        for main_category, subcategories in self.categories.items():
            for subcategory, category_code in subcategories.items():
                catalogue_code = self.get_catalogue_code(main_category)
                if catalogue_code:
                    yield scrapy.Request(url=self.products_api.format(category_code, self.page), headers=self.headers,
                                        meta={'category': main_category, 'sub_category': subcategory, 'category_code': category_code, 'page': self.page, 'catalogue_code': catalogue_code})

            

    def parse(self, response):
        item = ProductItemCarrefour()
        item['CatalogueName'] = response.meta['category']
        item['CategoryName'] = response.meta['sub_category']
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
                if not item['Offer']:
                    item['Offer'] = 0
                item['Offer'] = round(float(item['Offer']), 2)
                #sub_category = product.get('productCategoriesHearchi')
                #item['CategoryName'] = sub_category.split("/")[-1]
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
                                 meta={'category': item['CatalogueName'], 'sub_category': item['CategoryName'], 'category_code': category_code, 'page': page, 'catalogue_code': catalogue_code})
            
