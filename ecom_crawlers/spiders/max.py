import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemMax
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import mysql.connector




class MaxSpider(Spider):
    name = 'max'
    allowed_domains = ['www.maxfashion.com', '3hwowx4270-dsn.algolia.net']
    main_url = 'https://www.maxfashion.com/ae/en'
    products_api = 'https://3hwowx4270-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.22.1)%3B%20Browser'
    headers = {'Content-Type': 'application/json', 'X-Algolia-Api-Key': '4c4f62629d66d4e9463ddb94b9217afb', 'X-Algolia-Application-Id': '3HWOWX4270'}
    body = {"requests":[{"indexName":"prod_uae_max_Product","query":"","params":"facets=*&page={}&hitsPerPage=48&attributesToRetrieve=inStock%2Cconcept%2Ccolor%2CmanufacturerName%2Curl%2CreviewAvgRating%2C333WX493H%2C345WX345H%2C505WX316H%2C550WX550H%2C499WX739H%2Cbadge%2CbaseProductId%2Cname%2Csummary%2CwasPrice%2Cprice%2CemployeePrice%2CshowMoreColor%2CproductType%2CchildDetail%2Csibiling%2CthumbnailImg%2CgallaryImages%2CisConceptDelivery%2CextProdType%2CextProdCode%2CitemType%2CflashSaleData%2CcategoryName&attributesToHighlight=%5B%22name%22%5D&maxValuesPerFacet=1000&getRankingInfo=true&facetFilters=%5B%22inStock%3A1%22%2C%22approvalStatus%3A1%22%2C%5B%22allCategories%3{}%22%5D%5D&numericFilters=%5B%22price%20%3E%200%22%5D&clickAnalytics=true&analyticsTags=%5B%22en%22%2C%22Desktop%22%5D"}]}
    #Just make page and category name dynamic in body

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }
    page = 0
    count = 0
    
            

    categories = {
                  'Personal Care & Beauty': {
                      'Makeup & Accessories': 'Alsbeauty',
                  },

                  'Baby & Kids': {
                      'Girls Clothing': 'Amxkids-babygirlzerototwoyrs-clothing',
                      'Girls Clothing': 'Amxkids-girlstwotoeightyrs-clothing',
                      'Girls Clothing': 'Amxkids-girlseighttosixteenyrs-clothing',
                      'Girls Shoes': 'Amxkids-babygirlzerototwoyrs-shoes',
                      'Girls Shoes': 'Amxkids-girlstwotoeightyrs-shoes',
                      'Girls Shoes': 'Amxkids-girlseighttosixteenyrs-shoes',
                      
                      'Boys Clothing': 'Amxkids-babyboyzerototwoyrs-clothing',
                      'Boys Clothing': 'Amxkids-boystwotoeightyrs-clothing',
                      'Boys Clothing': 'Amxkids-boyseighttosixteenyrs-clothing',
                      'Boys Shoes': 'Amxkids-babyboyzerototwoyrs-shoes',
                      'Boys Shoes': 'Amxkids-boystwotoeightyrs-shoes',
                      'Boys Shoes': 'Amxkids-boyseighttosixteenyrs-shoes',

                      'Boys Accessories': 'Amxkids-accessories-boys',
                      'Girls Accessories': 'Amxkids-accessories-girls',
                      'Toys': 'Amxkids-toys'
                  },

                  'Furniture, Home And Garden': {
                      'Home Decor And Accessories': 'Ahbxbedroom',
                      'Home Decor And Accessories': 'Ahbxdecorandfurnishings',
                      'Home Decor And Accessories': 'Ahbxdiningroom',
                      'Home Decor And Accessories': 'Ahbxlivingroom',
                      'Home Decor And Accessories': 'Ahbxkitchen',
                      'Home Decor And Accessories': 'Ahbxbathroom',
                      'Home Decor And Accessories': 'Amxhome',
                      'Outdoor': 'Ahbxoutdoor',
                      'Furniture': 'Ahbxfurniture'
                  },
                  
                  'Fashion': {
                      'Women Clothing': 'Amxwomen-clothing',
                      'Women Clothing': 'Amxurbnwomen-clothing',
                      'Women Shoes': 'Amxwomen-shoes',
                      'Women Shoes': 'Amxurbnwomen-shoes',
                      'Women Bags': 'Amxwomen-bagsandwallets',
                      
                      'Women Accessories': 'Amxwomen-accessories',
                      'Women Accessories': 'Amxwomen-beauty',
                      'Women Accessories': 'Amxurbnwomen-accessories',
                      'Women Accessories': 'Amxurbnwomen-beauty',

                      'Men Clothing': 'Amxmen-clothing',
                      'Men Clothing': 'Amxurbnmen-clothing',
                      'Men Shoes': 'Amxmen-shoes',
                      'Men Shoes': 'Amxurbnmen-clothing',
                      'Men Bags': 'Amxmen-bagsandwallets',
                      'Men Bags': 'Amxurbnmen-bagsandwallets',
                      'Men Accessories': 'Amxmen-accessories',
                      'Men Accessories': 'Amxurbnmen-accessories'
                  },

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
        for main_category, sub_categories in self.categories.items():
            for sub_category, category_code in sub_categories.items():
                catalogue_code = self.get_catalogue_code(main_category)
                if catalogue_code:
                    print("########################################", sub_category)
                    # Create a deep copy of the original body
                    modified_body = copy.deepcopy(self.body)      
                    # Modify the copy with the current category
                    format_body = modified_body["requests"][0]["params"].format(self.page, category_code)
                    modified_body["requests"][0]["params"] = format_body
                    body = json.dumps(modified_body)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, callback=self.parse, meta={'category': main_category, 'sub_category': sub_category, 'category_code': category_code, 'page': self.page, 'vendor_code': self.vendor_code, 'catalogue_code': catalogue_code})


    
    def parse(self, response):
        item = ProductItemMax()
        vendor_code = response.meta['vendor_code']
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        category_code = response.meta['category_code']
        print("Category: ", category)
        page = response.meta['page']
        data = json.loads(response.text)
        results = data.get('results', [])
        for result in results:
            hits = result.get('hits', [])
            if hits:
                self.count = 0
                for hit in hits:
                    item['ProductName'] = hit.get('name', {}).get('en')
                    item['BrandName'] = hit.get('manufacturerName', {}).get('en')
                    item['CatalogueName'] = category
                    #category_key = next(iter(hit.get('url', {}).keys()))
                    item['CategoryName'] = sub_category
                    item['StockAvailability'] = hit.get('inStock')
                    item['RatingValue'] = hit.get('reviewAvgRating', {}).get('avgProductRating', 0)
                    item['RatingValue'] = round(float(item['RatingValue']), 2)
                    item['MainImage'] = hit.get('gallaryImages', [])[0]
                    item['Offer'] = hit.get('price')
                    item['Offer'] = round(float(item['Offer']), 2)
                    item['RegularPrice'] = hit.get('wasPrice', 0)
                    item['RegularPrice'] = round(float(item['RegularPrice']), 2)
                    if item['Offer'] == item['RegularPrice']:
                        item['Offer'] = 0
                    #badge = hit.get('badge', [])
                    #if badge:
                    #    item['badge'] = badge[-1].get('title', {}).get('en', '')
                    #else:
                    #    item['badge'] = ''
                    #item['description'] = hit.get('summary', {}).get('en', '')

                    url = next(iter(hit.get('url', {}).values()), "")
                    url = url.get('en', '')
                    item['URL'] = self.main_url + url
                    item['SKU'] = hit.get('objectID')
                    #item['page'] = page

                    item['BrandCode']= ''
                    item['ModelNumber']= ''
                    item['VendorCode']= vendor_code
                    catalogue_code = response.meta['catalogue_code']
                    category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                    item['CatalogueCode']= catalogue_code
                    item['CategoryCode']= category_code
                    
                    self.count+=1
                    yield item
                
                print("Category = {}, Total Products = {} on Page = {}".format(category, self.count, page))
                page = page + 1
                modified_body = copy.deepcopy(self.body)      
                format_body = modified_body["requests"][0]["params"].format(page, category_code)
                modified_body["requests"][0]["params"] = format_body
                body = json.dumps(modified_body)
                yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category':category, 'sub_category': sub_category, 'category_code': category_code, 'page': page, 'vendor_code': vendor_code, 'catalogue_code': catalogue_code})
