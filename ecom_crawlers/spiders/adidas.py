import re
import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemAdidas
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import mysql.connector



class AdidasOldSpider(Spider):
    name = 'adidas_old'
    allowed_domains = ['adidas.com']
    main_url = 'https://www.adidas.com'
    products_api = 'https://www.adidas.com/api/plp/content-engine?sitePath=us&query={}&start={}'
    review_api = 'https://www.adidas.com/api/models/{}/reviews?bazaarVoiceLocale=en_US&feature&includeLocales=en%2A&limit=10&offset=0&sort=newest'

    
    headers = {
        'authority': 'www.adidas.com',
        'method': 'GET',
        #'path': '/api/plp/content-engine?sitePath=us&query=men&start=48',
        'scheme': 'https',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'Glassversion': 'e592f42',
        'Pragma': 'no-cache',
        #'Referer': 'https://www.adidas.com/us/men?grid=true&start=48',
        #'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        #'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'X-Instana-L': '1,correlationType=web;correlationId=7477d05a502fc1aa',
        'X-Instana-S': '7477d05a502fc1aa',
        'X-Instana-T': '7477d05a502fc1aa'
    }
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    start = 0
    page = 0
    count = 0
    
    categories = {
        'Men': 'men',
        'Women': 'women',
        'Kids': 'kids',
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
        for category, formatted_category in self.categories.items():
            # catalogue_code = self.get_catalogue_code(category)
            # if catalogue_code:
            yield scrapy.Request(url=self.products_api.format(formatted_category, self.start), headers=self.headers, callback=self.parse, meta={'category': category, 'formatted_category': formatted_category, 'start': self.start, 'page': self.page})


    def parse(self, response):
        category = response.meta['category']
        formatted_category = response.meta['formatted_category']
        vendor_code = self.vendor_code
        start = response.meta['start']
        page = response.meta['page']
        data = json.loads(response.text)
        items = data.get('raw', {}).get('itemList', {}).get('items', [])
        if items:
            for item in items:
                name = item.get('displayName', '')
                sub_category = item.get('category', '')
                orderable = item.get('orderable', 1)
                rating = item.get('rating', 0)
                if not rating:
                    rating = 0
                img = item.get('image', {}).get('src', '')
                model_id = item.get('modelId', '')
                price_in_dollars = item.get('price', 0)
                sale_price_in_dollars = item.get('salePrice', 0)
                sale_percentage = item.get('salePercentage', '')
                url = self.main_url + item.get('link', '')

                yield scrapy.Request(url=self.review_api.format(model_id), headers=self.headers, callback=self.parse_review, meta={
                    'name': name,
                    'sub_category': sub_category,
                    'orderable': orderable,
                    'rating': rating,
                    'img': img,
                    'model_id': model_id,
                    'price_in_dollars': price_in_dollars,
                    'sale_price_in_dollars': sale_price_in_dollars,
                    'sale_percentage': sale_percentage,
                    'url': url,
                    'category': category,
                    'VendorCode': vendor_code,
                    'page': page
                })

            #Next Page
            start = start + 48
            page = page + 1
            yield scrapy.Request(url=self.products_api.format(formatted_category, start), headers=self.headers, callback=self.parse, meta={'category': category, 'formatted_category': formatted_category, 'start': start, 'page': page})




    def parse_review(self, response):
        item = ProductItemAdidas()
        item['ProductName'] = response.meta['name']
        item['CategoryName'] = response.meta['sub_category']
        item['StockAvailability'] = response.meta['orderable']
        item['RatingValue'] = response.meta['rating']
        item['MainImage'] = response.meta['img']
        item['SKU'] = response.meta['model_id']
        item['RegularPrice'] = response.meta['price_in_dollars']
        item['Offer'] = response.meta['sale_price_in_dollars']
        #item['sale_percentage'] = response.meta['sale_percentage']
        item['URL'] = response.meta['url']
        item['CatalogueName'] = response.meta['category']
        #item['page'] = response.meta['page']
        item['BrandName'] = ''
        item['BrandCode'] = ''
        item['ModelNumber'] = ''
        # catalogue_code = self.get_catalogue_code(item['CatalogueName'])
        # category_code = self.get_category_code(item['CategoryName'], catalogue_code)
        # item['CatalogueCode'] = catalogue_code
        # item['CategoryCode'] = category_code
        item['VendorCode'] = response.meta['VendorCode']

        item_reviews = []

        data = json.loads(response.text)
        reviews = data.get('reviews', [])
        if reviews:
            for review in reviews:
                comment = review.get('text')
                source = ''
                comment_date = review.get('submissionTime', '')
                comment_date = datetime.strptime(comment_date, '%Y-%m-%dT%H:%M:%S.%f%z')
                comment_date = comment_date.strftime('%Y-%m-%d')
                rating = round(float(review.get('rating')), 2)
                max_rating = round(float(review.get('ratingRange')), 2)

                review_data = {
                    'Comment': comment,
                    'Source': source,
                    'CommentDate': comment_date,
                    'rating': rating,
                    'max_rating': max_rating,
                    'average_rating': rating
                }
                item_reviews.append(review_data)
            item['reviews'] = item_reviews

        else:
            pass

        yield item


    