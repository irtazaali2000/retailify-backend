import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemBoots
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import mysql.connector



class BootsSpider(Spider):
    name = 'boots'
    allowed_domains = ['ae.boots.com', 'lqe0c6vcy3-dsn.algolia.net', 'api.bazaarvoice.com']
    main_url = 'https://ae.boots.com'
    
    products_api = 'https://lqe0c6vcy3-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)&x-algolia-application-id=LQE0C6VCY3&x-algolia-api-key=f12de14eaa992a4ae3a13f40b61c3978'
    reviews_api = 'https://api.bazaarvoice.com/data/reviews.json?apiversion=5.4&passkey=caOOUBjtmLXYYQujaGJhqJJ3zdusKlG5kVOAJcJeaqPdA&locale=en_AE&filter=productid:{}&filter=contentlocale:en*,ar*&Include=Products,Comments&Stats=Reviews&FilteredStats=Reviews&offset={}'
    #Takes SKU as Parameter

    headers = {'Content-Type': 'application/json'}
    body_skincare = {"requests":[{"indexName":"01live_bpae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Skincare%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22shop_by_department__skincare%22%2C%22shop_by_department%22%2C%22web__shop_by_department__skincare%22%2C%22web__shop_by_department%22%5D"}]}
    body_hairs = {"requests":[{"indexName":"01live_bpae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Hair%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__hair%22%2C%22shop_by_department%22%2C%22web__shop_by_department__hair%22%2C%22web__shop_by_department%22%5D"}]}
    body_personalcare_men = {"requests":[{"indexName":"01live_bpae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_gender.en%3ABoys%22%2C%22attr_gender.en%3AMen%22%2C%22attr_gender.en%3AUnisex%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Personal%20Care%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__personal_care%22%2C%22shop_by_department%22%2C%22web__shop_by_department__personal_care%22%2C%22web__shop_by_department%22%5D&userToken=anonymous-0e53accc-fb96-44e3-879a-da2462115d6a&analytics=true"},{"indexName":"01live_bpae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_gender.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Personal%20Care%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__personal_care%22%2C%22shop_by_department%22%2C%22web__shop_by_department__personal_care%22%2C%22web__shop_by_department%22%5D&userToken=anonymous-0e53accc-fb96-44e3-879a-da2462115d6a"}]}
    body_personalcare_women = {"requests":[{"indexName":"01live_bpae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_gender.en%3AGirls%22%2C%22attr_gender.en%3AUnisex%22%2C%22attr_gender.en%3AWomen%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Personal%20Care%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__personal_care%22%2C%22shop_by_department%22%2C%22web__shop_by_department__personal_care%22%2C%22web__shop_by_department%22%5D&userToken=anonymous-0e53accc-fb96-44e3-879a-da2462115d6a&analytics=true"},{"indexName":"01live_bpae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_gender.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Personal%20Care%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__personal_care%22%2C%22shop_by_department%22%2C%22web__shop_by_department__personal_care%22%2C%22web__shop_by_department%22%5D&userToken=anonymous-0e53accc-fb96-44e3-879a-da2462115d6a"}]}
    body_makeup = {"requests":[{"indexName":"01live_bpae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Makeup%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__makeup%22%2C%22shop_by_department%22%2C%22web__shop_by_department__makeup%22%2C%22web__shop_by_department%22%5D"}]}
    body_fragrance = {"requests":[{"indexName":"01live_bpae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Fragrance%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__fragrance%22%2C%22shop_by_department%22%2C%22web__shop_by_department__fragrance%22%2C%22web__shop_by_department%22%5D"}]}
    body_suncare_tanning = {"requests":[{"indexName":"01live_bpae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Suncare%20%26%20Tanning%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__suncare_tanning%22%2C%22shop_by_department%22%2C%22web__shop_by_department__suncare_tanning%22%2C%22web__shop_by_department%22%5D"}]}
    body_baby = {"requests":[{"indexName":"01live_bpae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Baby%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__baby%22%2C%22shop_by_department%22%2C%22web__shop_by_department__baby%22%2C%22web__shop_by_department%22%5D"}]}
    body_electrical = {"requests":[{"indexName":"01live_bpae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Electricals%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__electricals%22%2C%22shop_by_department%22%2C%22web__shop_by_department__electricals%22%2C%22web__shop_by_department%22%5D"}]}
    body_wellness = {"requests":[{"indexName":"01live_bpae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Wellness%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__wellness%22%2C%22shop_by_department%22%2C%22web__shop_by_department__wellness%22%2C%22web__shop_by_department%22%5D"}]}
    body_pharmacy = {"requests":[{"indexName":"01live_bpae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Pharmacy%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__pharmacy%22%2C%22shop_by_department%22%2C%22web__shop_by_department__pharmacy%22%2C%22web__shop_by_department%22%5D"}]}
    body_opticians = {"requests":[{"indexName":"01live_bpae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Opticians%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__opticians%22%2C%22shop_by_department%22%2C%22web__shop_by_department__opticians%22%2C%22web__shop_by_department%22%5D"}]}
    #body_gifting = {"requests":[{"indexName":"01live_bpae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Shop%20by%20Department%20%3E%20Gifting%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page=0&ruleContexts=%5B%22shop_by_department__gifting%22%2C%22shop_by_department%22%2C%22web__shop_by_department__gifting%22%2C%22web__shop_by_department%22%5D"}]}

    page = 0
    offset = 0
    count = 0

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }


    next_page_body_skincare = body_skincare["requests"][0]["params"].format(page)
    body_skincare["requests"][0]["params"] = next_page_body_skincare

    next_page_body_hairs = body_hairs["requests"][0]["params"].format(page)
    body_hairs["requests"][0]["params"] = next_page_body_hairs

    next_page_body_personalcare_men = body_personalcare_men["requests"][0]["params"].format(page)
    body_personalcare_men["requests"][0]["params"] = next_page_body_personalcare_men

    next_page_body_personalcare_women = body_personalcare_women["requests"][0]["params"].format(page)
    body_personalcare_women["requests"][0]["params"] = next_page_body_personalcare_women

    next_page_body_makeup = body_makeup["requests"][0]["params"].format(page)
    body_makeup["requests"][0]["params"] = next_page_body_makeup

    next_page_body_fragrance = body_fragrance["requests"][0]["params"].format(page)
    body_fragrance["requests"][0]["params"] = next_page_body_fragrance

    next_page_body_suncare_tanning = body_suncare_tanning["requests"][0]["params"].format(page)
    body_suncare_tanning["requests"][0]["params"] = next_page_body_suncare_tanning

    next_page_body_baby = body_baby["requests"][0]["params"].format(page)
    body_baby["requests"][0]["params"] = next_page_body_baby

    next_page_body_electrical = body_electrical["requests"][0]["params"].format(page)
    body_electrical["requests"][0]["params"] = next_page_body_electrical

    next_page_body_wellness = body_wellness["requests"][0]["params"].format(page)
    body_wellness["requests"][0]["params"] = next_page_body_wellness

    next_page_body_pharmacy = body_pharmacy["requests"][0]["params"].format(page)
    body_pharmacy["requests"][0]["params"] = next_page_body_pharmacy

    next_page_body_opticians = body_opticians["requests"][0]["params"].format(page)
    body_opticians["requests"][0]["params"] = next_page_body_opticians

    # next_page_body_gifting = body_gifting["requests"][0]["params"].format(page)
    # body_gifting["requests"][0]["params"] = next_page_body_gifting

    
    item_reviews = []

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
        # categories = {
        #     'body_skincare': 'skin_care',
        #     'body_hairs': 'hairs',
        #     'body_personalcare': 'personal_care',
        #     'body_makeup': 'makeup',
        #     'body_fragrance': 'fragrance',
        #     'body_suncare_tanning': 'suncare_tanning',
        #     'body_baby': 'baby',
        #     'body_electrical': 'electrical',
        #     'body_wellness': 'wellness',
        #     'body_pharmacy': 'pharmacy',
        #     'body_opticians': 'opticians',
        #     # 'body_gifting': 'gifting'
        # }

        categories = {
                        'body_skincare': {'Personal Care & Beauty': 'Makeup & Accessories'},
                        'body_hairs': {'Personal Care & Beauty': 'Makeup & Accessories'},
                        'body_personalcare_men': {'Personal Care & Beauty': 'Personal Care For Men'},
                        'body_personalcare_women': {'Personal Care & Beauty': 'Personal Care For Women'},
                        'body_makeup': {'Personal Care & Beauty': 'Makeup & Accessories'},
                        'body_fragrance': {'Personal Care & Beauty': 'Fragrances & Perfumes'},
                        'body_suncare_tanning': {'Personal Care & Beauty': 'Makeup & Accessories'},
                        'body_baby': {'Baby & Kids': 'Diapers, Bath & Skincare'},
                        'body_electrical': {'Health & Medical': 'Mouth Care'},
                        'body_wellness': {'Health & Medical': 'Medicine'},
                        'body_pharmacy': {'Health & Medical': 'Medicine'},
                        'body_opticians': {'Health & Medical': 'Medicine'}
                     }

        for body, category_data in categories.items():
            category, subcategory = list(category_data.keys())[0], list(category_data.values())[0]
            catalogue_code = self.get_catalogue_code(category)
            if catalogue_code:
                request_body = getattr(self, body)
                yield scrapy.Request(
                    url=self.products_api,
                    method='POST',
                    headers=self.headers,
                    body=json.dumps(request_body),
                    callback=self.parse,
                    meta={'category': category, 'sub_category': subcategory, 'catalogue_code': catalogue_code, 'page': self.page}
                )

        

    def parse(self, response):
        print("###################################Inside PARSE###################################")
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        catalogue_code = response.meta['catalogue_code']
        page = response.meta['page']
        print("Category = {}, Page = {}".format(category, page))
        data = json.loads(response.text)
        results = data.get('results', [])
        self.count = 0
        for result in results:
            hits = result.get('hits', [])
            if hits:        
                for hit in hits:
                    title = hit.get('title', {}).get('en')
                    sku = hit.get('sku')
                    # sub_category = hit.get('gtm', {}).get('gtm-category')
                    price = hit.get('gtm', {}).get('gtm-price')
                    old_price = hit.get('gtm', {}).get('gtm-old-price', 0)
                    description = hit.get('body', {}).get('en')
                    media = hit.get('media', [])
                    image = ''
                    if media:
                        image = media[0].get('url')
                    url = hit.get('url', {}).get('en')
                    url = self.main_url+url
                    stock_quantity = hit.get('stock_quantity')
                    in_stock = hit.get('in_stock', {}).get('en')
                    rating = hit.get('attr_bv_average_overall_rating', {}).get('en', 0)
                    brand_name = hit.get('gtm', {}).get('gtm-brand', '')
                    vendor_code = self.vendor_code
                    catalogue_code = response.meta['catalogue_code']
                    category_code = self.get_category_code(sub_category, catalogue_code)
                
                    yield scrapy.Request(url=self.reviews_api.format(sku, self.offset), headers=self.headers, callback=self.parse_review, meta={
                        'title':title,
                        'sku':sku,
                        'sub_category':sub_category,
                        'price':price,
                        'old_price':old_price,
                        'description':description,
                        'image':image,
                        'url':url,
                        'stock_quantity':stock_quantity,
                        'in_stock':in_stock,
                        'category':category,
                        'brand_name': brand_name,
                        'vendor_code': vendor_code,
                        'CatalogueCode': catalogue_code,
                        'CategoryCode': category_code,
                        'rating': rating,
                        'page':page
                    })

                #Next Page
                page = page + 1

                if category == 'Personal Care & Beauty':
                    next_page_body = self.body_skincare["requests"][0]["params"]
                    next_page_body = next_page_body.replace(f'page={page-1}', f'page={page}')
                    self.body_skincare["requests"][0]["params"] = next_page_body
                    body = json.dumps(self.body_skincare)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category': category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': page})

                # elif category == 'hairs':
                    next_page_body = self.body_hairs["requests"][0]["params"]
                    next_page_body = next_page_body.replace(f'page={page-1}', f'page={page}')
                    self.body_hairs["requests"][0]["params"] = next_page_body
                    body = json.dumps(self.body_hairs)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category': category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': page})

                #elif category == 'personal_care':
                    next_page_body = self.body_personalcare_men["requests"][0]["params"]
                    next_page_body = next_page_body.replace(f'page={page-1}', f'page={page}')
                    self.body_personalcare_men["requests"][0]["params"] = next_page_body
                    body = json.dumps(self.body_personalcare_men)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category': category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': page})

                #elif category == 'personal_care':
                    next_page_body = self.body_personalcare_women["requests"][0]["params"]
                    next_page_body = next_page_body.replace(f'page={page-1}', f'page={page}')
                    self.body_personalcare_women["requests"][0]["params"] = next_page_body
                    body = json.dumps(self.body_personalcare_women)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category': category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': page})
                
                
                #elif category == 'makeup':
                    next_page_body = self.body_makeup["requests"][0]["params"]
                    next_page_body = next_page_body.replace(f'page={page-1}', f'page={page}')
                    self.body_makeup["requests"][0]["params"] = next_page_body
                    body = json.dumps(self.body_makeup)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category': category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': page})

                #elif category == 'fragrance':
                    next_page_body = self.body_fragrance["requests"][0]["params"]
                    next_page_body = next_page_body.replace(f'page={page-1}', f'page={page}')
                    self.body_fragrance["requests"][0]["params"] = next_page_body
                    body = json.dumps(self.body_fragrance)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category': category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': page})

                #elif category == 'suncare_tanning':
                    next_page_body = self.body_suncare_tanning["requests"][0]["params"]
                    next_page_body = next_page_body.replace(f'page={page-1}', f'page={page}')
                    self.body_suncare_tanning["requests"][0]["params"] = next_page_body
                    body = json.dumps(self.body_suncare_tanning)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category': category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': page})

                elif category == 'Baby & Kids':
                    next_page_body = self.body_baby["requests"][0]["params"]
                    next_page_body = next_page_body.replace(f'page={page-1}', f'page={page}')
                    self.body_baby["requests"][0]["params"] = next_page_body
                    body = json.dumps(self.body_baby)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category': category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': page})

                elif category == 'Health & Medical':
                    next_page_body = self.body_electrical["requests"][0]["params"]
                    next_page_body = next_page_body.replace(f'page={page-1}', f'page={page}')
                    self.body_electrical["requests"][0]["params"] = next_page_body
                    body = json.dumps(self.body_electrical)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category': category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': page})

                #elif category == 'Health & Medical':
                    next_page_body = self.body_wellness["requests"][0]["params"]
                    next_page_body = next_page_body.replace(f'page={page-1}', f'page={page}')
                    self.body_wellness["requests"][0]["params"] = next_page_body
                    body = json.dumps(self.body_wellness)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category': category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': page})

                #elif category == 'pharmacy':
                    next_page_body = self.body_pharmacy["requests"][0]["params"]
                    next_page_body = next_page_body.replace(f'page={page-1}', f'page={page}')
                    self.body_pharmacy["requests"][0]["params"] = next_page_body
                    body = json.dumps(self.body_pharmacy)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category':category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': page})

                #elif category == 'opticians':
                    next_page_body = self.body_opticians["requests"][0]["params"]
                    next_page_body = next_page_body.replace(f'page={page-1}', f'page={page}')
                    self.body_opticians["requests"][0]["params"] = next_page_body
                    body = json.dumps(self.body_opticians)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category': category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'page': page})

                # elif category == 'gifting':
                #     next_page_body = self.body_gifting["requests"][0]["params"]
                #     next_page_body = next_page_body.replace(f'page={page-1}', f'page={page}')
                #     self.body_gifting["requests"][0]["params"] = next_page_body
                #     body = json.dumps(self.body_gifting)
                #     yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category': 'gifting', 'catalogue_code': catalogue_code, 'page': page})


    def parse_review(self, response):
        item = ProductItemBoots()
        item['ProductName'] = response.meta['title']
        item['CategoryName'] = response.meta['sub_category']
        vendor_code = response.meta['vendor_code']
        avg_rating = response.meta['rating']
        item['Offer'] = response.meta['price']
        item['Offer'] = round(float(item['Offer']), 2)
        item['RegularPrice'] = response.meta['old_price']
        item['RegularPrice'] = round(float(item['RegularPrice']), 2)
        
        #item['description'] = response.meta['description']
        item['MainImage'] = response.meta['image']
        item['URL'] = response.meta['url']
        #item['stock_quantity'] = response.meta['stock_quantity']
        item['StockAvailability'] = response.meta['in_stock']
        item['CatalogueName'] = response.meta['category']
        item['BrandName'] = response.meta['brand_name']
        item['BrandCode'] = ''
        item['ModelNumber'] = ''
        item['VendorCode'] = vendor_code
        #item['page'] = response.meta['page']
        #item['review'] = review
        item['RatingValue'] = avg_rating
        item['RatingValue'] = round(float(item['RatingValue']), 2)
        item['CatalogueCode']= response.meta['CatalogueCode']
        item['CategoryCode']= response.meta['CategoryCode']
        # item['reviews'] = item_reviews
        item['SKU'] = response.meta['sku']
        
        
        data = json.loads(response.text)
        results = data.get('Results', [])
        item_reviews = []

        if results:
            for review in results:
                review_text = review.get('ReviewText', '')
                source = review.get('SourceClient',  '')
                comment_date = review.get('LastModeratedTime', '')
                comment_date = datetime.strptime(comment_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                comment_date = comment_date.strftime("%Y-%m-%d")
                rating = review.get('Rating')
                max_rating = review.get('RatingRange')

                review_data = {
                        'Comment': review_text,
                        'Source': source,
                        'CommentDate': comment_date,
                        'rating': rating,
                        'max_rating': max_rating,
                        'average_rating': avg_rating
                        }
                item_reviews.append(review_data)
            item['reviews'] = item_reviews
        else:
            pass

        yield item
            #Next Page
            # if next_page_url:
            #     yield scrapy.Request(url=next_page_url, callback=self.parse_review, meta={'item': item})
