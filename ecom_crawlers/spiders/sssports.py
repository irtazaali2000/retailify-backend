import re
import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemSunAndSandSports
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import mysql.connector



class SunAndSandSportsSpider(Spider):
    name = 'sssports'
    allowed_domains = ['en-ae.sssports.com']
    main_url = 'https://en-ae.sssports.com'
    #product_url_men = 'https://en-ae.sssports.com/mens'
    #product_url_women = 'https://en-ae.sssports.com/womens'
    
    cat_products_urls = {
            'Fashion': {
                'Men Clothing': 'https://en-ae.sssports.com/mens/clothing?pmin=0,01&prefn1=gender&prefv1=Mens|Unisex&gs=3&srule=featured',
                'Men Shoes': 'https://en-ae.sssports.com/mens/shoes?pmin=0,01&prefn1=gender&prefv1=Mens|Unisex&gs=3&srule=featured',
                'Men Accessories': 'https://en-ae.sssports.com/mens/accessories?pmin=0,01&prefn1=gender&prefv1=Mens|Unisex&gs=3&srule=featured',
                
                'Women Clothing': 'https://en-ae.sssports.com/womens/clothing?pmin=0,01&prefn1=gender&prefv1=Womens|Unisex&gs=3&srule=featured',
                'Women Shoes': 'https://en-ae.sssports.com/womens/shoes?pmin=0,01&prefn1=gender&prefv1=Womens|Unisex&gs=3&srule=featured',
                'Women Accessories': 'https://en-ae.sssports.com/womens/accessories?pmin=0,01&prefn1=gender&prefv1=Womens|Unisex&gs=3&srule=featured'
            
            },

            'Baby & Kids': {
                'Boys Clothing': 'https://en-ae.sssports.com/kids/clothing?pmin=0,01&prefn1=gender&prefv1=Kids&prefn2=kidsGender&prefv2=Unisex|Boys&gs=3&srule=featured',
                'Boys Shoes': 'https://en-ae.sssports.com/kids/shoes?pmin=0,01&prefn1=gender&prefv1=Kids&prefn2=kidsGender&prefv2=Unisex|Boys&gs=3&srule=featured',
                'Boys Accessories': 'https://en-ae.sssports.com/kids/accessories?pmin=0,01&prefn1=gender&prefv1=Kids&prefn2=kidsGender&prefv2=Unisex|Boys&gs=3&srule=featured',

                'Girls Clothing': 'https://en-ae.sssports.com/kids/shoes?pmin=0,01&prefn1=gender&prefv1=Kids&prefn2=kidsGender&prefv2=Unisex|Girls&gs=3&srule=featured',
                'Girls Shoes': 'https://en-ae.sssports.com/kids/clothing?pmin=0,01&prefn1=gender&prefv1=Kids&prefn2=kidsGender&prefv2=Unisex|Girls&gs=3&srule=featured',
                'Girls Accessories': 'https://en-ae.sssports.com/kids/accessories?pmin=0,01&prefn1=gender&prefv1=Kids&prefn2=kidsGender&prefv2=Unisex|Girls&gs=3&srule=featured',
            },

            'Sports Equipment': {
                    'Cycling & Skating': 'https://en-ae.sssports.com/equipment/cycling?pmin=0,01&gs=3&srule=featured',
                    'Fitness': 'https://en-ae.sssports.com/equipment/fitness?pmin=0,01&gs=3&srule=featured',
                    'Rugby & Football': 'https://en-ae.sssports.com/equipment/football?pmin=0,01&gs=3&srule=featured',
                    'Basketball': 'https://en-ae.sssports.com/equipment/basketball?pmin=0,01&gs=3&srule=featured',
                    'Swimming': 'https://en-ae.sssports.com/equipment/swimming?pmin=0,01&gs=3&srule=featured',
                    'Volleyball': 'https://en-ae.sssports.com/equipment/volleyball?pmin=0,01&gs=3&srule=featured'
            },

            'Health & Medical': {
                'Nutrition': 'https://en-ae.sssports.com/health-and-nutrition'
            }
        }

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 200,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    page = 0
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
        self.vendor_code = raw_res.get('VendorCode')

    def get_catalogue_code(self, catalogue_name):
        query = "SELECT CatalogueCode FROM product_catalogue WHERE CatalogueName = %s"
        self.cursor.execute(query, (catalogue_name,))
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        else:
            insert_query = "INSERT INTO product_catalogue (CatalogueName) VALUES (%s)"
            self.cursor.execute(insert_query, (catalogue_name,))
            self.conn.commit()
            
            self.cursor.execute(query, (catalogue_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
    
    def get_category_code(self, category_name, catalogue_code):
        query = "SELECT CategoryCode FROM product_category WHERE CategoryName = %s"
        self.cursor.execute(query, (category_name,))
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        else:
            insert_query = "INSERT INTO product_category (CategoryName, CatalogueCode_id) VALUES (%s, %s)"
            self.cursor.execute(insert_query, (category_name, catalogue_code))
            self.conn.commit()

            self.cursor.execute(query, (category_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None


    def start_requests(self):
        for main_category, sub_categories in self.cat_products_urls.items():
            for sub_category, product_url in sub_categories.items():
                catalogue_code = self.get_catalogue_code(main_category)  # Assuming you have this method implemented
                if catalogue_code:
                    yield scrapy.Request(url=product_url, dont_filter=True, meta={'category': main_category, 'sub_category': sub_category, 'page': self.page, 'vendor_code': self.vendor_code, 'catalogue_code': catalogue_code})

    def parse(self, response):
        #print("INSIDE PARSE")
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        page = response.meta['page']
        catalogue_code = response.meta['catalogue_code']
        vendor_code = response.meta['vendor_code']
        products_container = response.css('.pdp-link')
        for product in products_container:
            url = product.css('a::attr(href)').get()
            url = self.main_url + url
            
            yield scrapy.Request(url=url, callback=self.parse_product, meta={'category': category, 'sub_category': sub_category, 'url': url, 'page': page, 'vendor_code': vendor_code, 'catalogue_code': catalogue_code})

        #NEXT PAGE
        load_more_url = response.css('.js-show-more-btn::attr(data-url)').get()
        if load_more_url:
            page = page + 1
            yield scrapy.Request(url=load_more_url, callback=self.parse, meta={'category': category, 'sub_category': sub_category, 'page': page, 'vendor_code': vendor_code, 'catalogue_code': catalogue_code})


    def parse_product(self, response):
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        page = response.meta['page']
        url = response.meta['url']
        vendor_code = response.meta['vendor_code']
    
        title = response.xpath('//span[@class="product-detail__product-name js-gtm-product-name"]/text()').get()
        title = title.strip()
        img = response.xpath('//img[@class="d-block img-fluid lazyload"][1]/@data-high-res-src').get()
        brand = response.xpath('//h1[@class="product-detail__product-brand-product-name"]/span[@class="product-detail__product-brand"]/text()').get()
        # sub_category = response.xpath('(//li[@class="breadcrumb__item"])[last()-1]/a/text()').get()
        # if sub_category:
        #     sub_category = sub_category.strip()
        price_in_aed = response.xpath('//span[@class="sales"]/span[@class="value"]/@content').get()
        price_in_aed = round(float(price_in_aed), 2)
        old_price_in_aed = response.xpath('//div[@class="prices js-gtm-price"]/div[@class="price"]/span/del/span[@class="strike-through list pl-1"]/span[@class="value"]/@content').get()
        old_price_in_aed = round(float(old_price_in_aed), 2)
        if not old_price_in_aed:
            old_price_in_aed = 0

        discount = response.xpath('//div[@class="prices js-gtm-price"]/div[@class="price"]/span/div[@class="discount-top-pdp"]/span[@class="discount-text d-block discount-pdp-text"]/text()').get()
        if not discount:
            discount = ''

        is_limited_stock = response.xpath('//span[@class="limited-stock"]/text()[normalize-space()]').get()
        if is_limited_stock:
            is_limited_stock = True
        else:
            is_limited_stock = False

        description = response.xpath('//div[@class="js-accordion-content accordion__content"]/p/text()').get()
        if not description:
            description = ''
        
        detail_list_items = response.xpath('//div[@class="js-accordion-content accordion__content"]/ul/li')
        list_item_array = []
        for list_item in detail_list_items:
            content = list_item.xpath('normalize-space(.)').get()
            list_item_array.append(content)
        if not list_item_array:
            list_item_array = ''

        type = response.xpath('//li[@class="js-more-info-specifications"]/span/text()').get()
        product_code = response.xpath('//li[@class="js-more-info-id"]/span/text()').get()

        catalogue_code = response.meta['catalogue_code']
        category_code = self.get_category_code(sub_category, catalogue_code)


        yield {
            'ProductName': title,
            'CatalogueName': category,
            'CategoryName': sub_category,
            #'is_limited_stock': is_limited_stock,
            'BrandName': brand,
            'BrandCode': '',
            'StockAvailability': 1,
            'ModelNumber': '',
            'RatingValue': 0,
            'Offer': price_in_aed,
            'RegularPrice': old_price_in_aed,
            #'discount': discount,
            #'description': description,
            #'product_elements': list_item_array,
            #'type': type,
            'SKU': product_code,
            'URL': url,
            'MainImage': img,
            'VendorCode': vendor_code,
            'CatalogueCode': catalogue_code,
            'CategoryCode': category_code

            #'page': page
        }





 

