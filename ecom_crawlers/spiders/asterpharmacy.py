import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemAsterPharmacy
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy




class AsterPharmacyOldSpider(Spider):
    name = 'asterpharmacy_old'
    allowed_domains = ['myaster.com']
    main_url = 'https://www.myaster.com/online-pharmacy'
    products_api = 'https://www.myaster.com/_next/data/ggs6cB2Foo3RIfGhdTHUd/online-pharmacy/c/{}.json?page={}'
    headers = {'Content-Type': 'application/json'}
    

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 200,
                #'LOG_STDOUT': False,
        #'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    page = 1
    count = 0
    
    categories = {
        'Mother and Baby': '3381',
        'Beauty': '3727',
        'Nutrition': '2058',
        'Equipment and Homecare': '1911',
        'Medical Essentials': '1822',
        'Skin Care': '4192',
        'Vitamin C': '4296',
        'Vitamin D': '4295',
        'Ramadan Essentials': '4189',
        'Lifestyle and Fitness': '1989'
        }

    
    def start_requests(self):
        for main_category, category_id in self.categories.items():
            formatted_products_api = self.products_api.format(category_id, self.page)
            yield scrapy.Request(url=formatted_products_api, headers=self.headers, callback=self.parse, meta={'category': main_category, 'category_id': category_id, 'page': self.page})


    def parse(self, response):
        item = ProductItemAsterPharmacy()
        category = response.meta['category']
        category_id = response.meta['category_id']
        page = response.meta['page']
        data = json.loads(response.text)
        facetResponse = data.get('pageProps', {}).get('facetResponse', {})
        products = facetResponse.get('data', [])
        if products:
            for product in products:
                item['title'] = product.get('name', '')
                item['sku'] = product.get('sku', '')
                item['price_in_aed'] = product.get('price', 0)
                item['offer_price_in_aed'] = product.get('special_price', 0)
                item['brand'] = product.get('brand')
                matching_categories_list = product.get('categoryDetails', [])
                lst = []
                if matching_categories_list:
                    for matching_category in matching_categories_list:
                        lst.append(matching_category.get('categoryName'))
                else:
                    item['matching_categories'] = ''

                item['matching_categories'] = lst
                item['quantity'] = product.get('quantity', 0)
                item['in_stock'] = product.get('inStock', True)
                item['rating'] = product.get('avgRating', 0)
                url = product.get('productUrl', '')
                item['url'] = self.main_url + url
                item['img'] = product.get('thumbnail_image', '')
                item['page'] = page
                item['category'] = category
                self.count+=1
                yield item
            
            print("Category = {}, Total Products = {} on Page = {}".format(category, self.count, page))
            #Next Page
            page = page + 1
            formatted_products_api = self.products_api.format(category_id, page)
            yield scrapy.Request(url=formatted_products_api, headers=self.headers, meta={'category': category, 'category_id': category_id, 'page': page})