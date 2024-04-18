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



class AdidasSpider(Spider):
    name = 'adidas'
    allowed_domains = ['adidas.ae', 'api.bazaarvoice.com'] 
    main_url = 'https://www.adidas.ae'
    review_api = 'https://api.bazaarvoice.com/data/reviews.json?resource=reviews&action=REVIEWS_N_STATS&filter=productid%3Aeq%3A{}&filter=contentlocale%3Aeq%3Aen*%2Cen_AE%2Cen_AE&filter=isratingsonly%3Aeq%3Afalse&filter_reviews=contentlocale%3Aeq%3Aen*%2Cen_AE%2Cen_AE&include=authors%2Cproducts%2Ccomments&filteredstats=reviews&Stats=Reviews&limit=3&offset=0&limit_comments=3&sort=relevancy%3Aa1&passkey=caJo6jPrbeNgniRJlgc116AoUTbGo2LVHawofYQqslZ7s&apiversion=5.5&displaycode=27341-en_ae'

    headers = {
        'authority': 'www.adidas.ae',
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
        'DOWNLOAD_DELAY': 0.5,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 200,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    start = 0
    page = 0
    count = 0
    

    
    categories = {'Men': {'Men Shoes': 'https://www.adidas.ae/en/men-shoes',
                          'Men Clothing': 'https://www.adidas.ae/en/men-clothing',
                          'Men Accessories': 'https://www.adidas.ae/en/men-accessories'
                          },
                   
                  'Women': {'Women Shoes': 'https://www.adidas.ae/en/women-shoes',
                            'Women Clothing': 'https://www.adidas.ae/en/women-clothing',
                            'Women Accessories': 'https://www.adidas.ae/en/women-accessories'},

                  'Kids': {'Infants and Toddlers Sportswear': 'https://www.adidas.ae/en/infant_todder',
                           'Kids 4 to 8 Years Sportswear': 'https://www.adidas.ae/en/kids_4_8_years',
                           'Kids 8 to 16 Years Sportswear': 'https://www.adidas.ae/en/kids_8_16_years',
                           'Kids Accessories': 'https://www.adidas.ae/en/kids-accessories'}

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
            catalogue_code = self.get_catalogue_code(main_category)
            if catalogue_code:
                for sub_category, sub_category_url in sub_categories.items():
                    yield scrapy.Request(url=sub_category_url, headers=self.headers, meta={'main_category': main_category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': self.page})

    def parse(self, response):
        main_category = response.meta['main_category']
        sub_category = response.meta['sub_category']
        catalogue_code = response.meta['catalogue_code']
        page = response.meta['page']
        vendor_code = self.vendor_code
        products_container = response.css('.link ')
        for product in products_container:
            url = product.css('a::attr(href)').get()
            url = self.main_url + url
            
            yield scrapy.Request(url=url, callback=self.parse_product, headers=self.headers, meta={'main_category': main_category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'vendor_code': vendor_code, 'url': url, 'page': page}) #'vendor_code': vendor_code})

        #NEXT PAGE
        load_more_url = response.xpath('//div[@class="show-next col-3 col-sm-2 text-right"]/button/@data-url').get()
        if load_more_url:
            page = page + 1
            yield scrapy.Request(url=load_more_url, headers=self.headers, callback=self.parse, meta={'main_category': main_category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': page})
                                 #, meta={'category': category, 'page': page, 'vendor_code': vendor_code})

    def parse_product(self, response):
        main_category = response.meta['main_category']
        sub_category = response.meta['sub_category']
        catalogue_code = response.meta['catalogue_code']
        vendor_code = response.meta['vendor_code']
        url = response.meta['url']
        sku = url.split('/')[-1].split('.')[0]
        title = response.xpath('//h1[@class="product-name "][1]/text()').get()
        offer = response.xpath("(//div[@class='prices ']/div[@class='price']/span/span[@class='sales']/span[@class='value'])[1]/text()").get()
        if offer:
            offer = offer.strip()
            offer = offer.replace(',', '')
            offer = round(float(offer.split()[1]), 2) 
        
        if not offer:
            offer = response.xpath("(//div[@class='prices']/div[@class='price']/span/span[@class='sales']/span[@class='value'])[1]/text()").get()
            if offer:
                offer = offer.strip()
                offer = offer.replace(',', '')
                offer = round(float(offer.split()[1]), 2) 

            if not offer:
                offer = 0
        
        
        regular_price = response.xpath("(//div[@class='prices ']/div[@class='price']/span/del/span[@class='strike-through list']/span[@class='value'])[1]/text()").get()
        if regular_price:
            regular_price = regular_price.strip()
            #regular_price = round(float(regular_price.split()[1]), 2)
        
        if not regular_price:
            regular_price = 0



        if regular_price == "":
            regular_price = 0

        #category = response.xpath("//a[@class='current']/text()").get()
        #category = category.strip()
        #rating = response.xpath('(//div[@class="bv_avgRating_component_container notranslate"])[1]/text()').get()
        
        
        yield scrapy.Request(url=self.review_api.format(sku), headers=self.headers, callback=self.parse_review, meta={
            'ProductName': title,
            'SKU': sku,
            'Offer': offer,
            'RegularPrice': regular_price,
            'CatalogueName': main_category,
            'CategoryName': sub_category,
            'URL': url,
            'vendor_code': vendor_code,
            'catalogue_code': catalogue_code
                })

        
    def parse_review(self, response):
        item = ProductItemAdidas()
        item['ProductName'] = response.meta['ProductName']
        item['CategoryName'] = response.meta['CategoryName']
        item['StockAvailability'] = 1
        item['SKU'] = response.meta['SKU']
        item['RegularPrice'] = response.meta['RegularPrice']
        item['Offer'] = response.meta['Offer']
        item['URL'] = response.meta['URL']
        item['CatalogueName'] = response.meta['CatalogueName']
        item['BrandName'] = ''
        item['BrandCode'] = ''
        item['ModelNumber'] = ''
        item['MainImage'] = ''
        catalogue_code = response.meta['catalogue_code']
        category_code = self.get_category_code(item['CategoryName'], catalogue_code)
        item['CatalogueCode'] = catalogue_code
        item['CategoryCode'] = category_code
        item['VendorCode'] = response.meta['vendor_code']
        item_reviews = []

        data = json.loads(response.text)
        item['RatingValue'] = round(float(data.get('Includes', {}).get('Products', {}).get(str(item['SKU']), {}).get('FilteredReviewStatistics', {}).get('AverageOverallRating', 0)), 2)
        reviews = data.get('Results', [])
        if reviews:
            for review in reviews:
                comment = review.get('ReviewText')
                source = review.get('SourceClient')
                comment_date = review.get('SubmissionTime', '')
                comment_date = datetime.strptime(comment_date, '%Y-%m-%dT%H:%M:%S.%f%z')
                comment_date = comment_date.strftime('%Y-%m-%d')
                rating = review.get('Rating')
                max_rating = round(float(review.get('RatingRange')), 2)

                review_data = {
                    'Comment': comment,
                    'Source': source,
                    'CommentDate': comment_date,
                    'rating': rating,
                    'max_rating': max_rating,
                    'average_rating': item['RatingValue']
                }
                item_reviews.append(review_data)
            item['reviews'] = item_reviews

        else:
            pass

        yield item