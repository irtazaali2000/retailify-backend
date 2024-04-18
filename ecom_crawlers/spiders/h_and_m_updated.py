import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemHandM
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import mysql.connector




class HandMSpider(Spider):
    name = 'h_and_m'
    allowed_domains = ['ae.hm.com', 'hgr051i5xn-dsn.algolia.net', 'api.bazaarvoice.com']
    main_url = 'https://ae.hm.com'
    products_api = 'https://hgr051i5xn-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)&x-algolia-application-id=HGR051I5XN&x-algolia-api-key=a2fdc9d456e5e714d8b654dfe1d8aed8'
    review_api = 'https://api.bazaarvoice.com/data/reviews.json?apiversion=5.4&passkey=caf5dGtwUGzhqIcWTSuBVjtbATWQvyCzylmXtoy02sbE8&locale=en_AE&filter=productid:{}&filter=contentlocale:en_KW,en_AE,en_SA,en_QA,en_EG,en_BH,ar_KW,ar_AE,ar_SA,ar_QA,ar_EG,ar_BH&Include=Products,Comments,Authors&Stats=Reviews&FilteredStats=Reviews&Limit=3&Offset=0&sort=IsFeatured:Desc,SubmissionTime:Desc,Helpfulness:Desc,Rating:Desc,Rating:Asc,HasPhotos:Desc'
    headers = {'Content-Type': 'application/json'}
    body = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters={}&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&analytics=true"}]}
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
    
    categories = {'Men': '(stock%20%3E%200)%20AND%20(field_category_name.en.lvl2%3A%20%22Men%20%3E%20Shop%20By%20Product%20%3E%20View%20All%22)',
                  'Women': '(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Women%20%3E%20Shop%20By%20Product%22)',
                  'Baby': '(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Baby%20%3E%20Shop%20by%20Product%22)',
                  'Kids': '(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Shop%20By%20Product%22)',
                  'Home': '(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22H%26M%20HOME%20%3E%20Shop%20By%20Product%22)',
                  'Beauty': '(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Beauty%20%3E%20Beauty%20Products%22)'}
                  #'Home': 'Ahbxhomeimprovement', 
                  #'Gift Card': 'Agiftcard'}
    
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
    #visited_urls = set()

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
        for category, category_code_f in self.categories.items():
            catalogue_code = self.get_catalogue_code(category)
            if catalogue_code:
                print("########################################", category)
                # Create a deep copy of the original body
                modified_body = copy.deepcopy(self.body)      
                # Modify the copy with the current category
                format_body = modified_body["requests"][0]["params"].format(category_code_f, self.page)
                modified_body["requests"][0]["params"] = format_body
                body = json.dumps(modified_body)
                yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, callback=self.parse, meta={'category':category, 'category_code_f': category_code_f, 'catalogue_code': catalogue_code, 'page':self.page})

    
    def parse(self, response):
        item = ProductItemHandM()
        vendor_code = self.vendor_code
        category = response.meta['category']
        category_code_f = response.meta['category_code_f']
        print("Category: ", category)
        page = response.meta['page']
        data = json.loads(response.text)
        results = data.get('results', [])
        for result in results:
            hits = result.get('hits', [])
            if hits:
                for hit in hits:
                    item['SKU'] = hit.get('gtm', {}).get('gtm-product-sku')
                    item['ProductName'] = hit.get('gtm', {}).get('gtm-name')
                    item['BrandName'] = hit.get('gtm', {}).get('gtm-brand')
                    if not item['BrandName']:
                        item['BrandName'] = ''
                    item['CatalogueName'] = category
                    
                    category_list3 = hit.get('lhn_category', {}).get('en', {}).get('lvl3', [])
                    if category_list3:
                        item['CategoryName'] = category_list3[0].split('>')[3]
                       
                    else:
                        category_list2 = hit.get('lhn_category', {}).get('en', {}).get('lvl2', [])
                        if category_list2:
                            item['CategoryName'] = category_list2[0].split('>')[2]
               
                        else:
                            category_list1 = hit.get('lhn_category', {}).get('en', {}).get('lvl1', [])
                            if category_list1:
                                item['CategoryName'] = category_list1[0].split('>')[1]
   
                            else:
                                category_list0 = hit.get('lhn_category', {}).get('en', {}).get('lvl0', [])
                                if category_list0:
                                    item['CategoryName'] = category_list0[0].split('>')[0]
                    

                    if not item['CategoryName']:
                        item['CategoryName'] = item['CatalogueName']



                    item['StockAvailability'] = hit.get('in_stock')
                    item['RatingValue'] = round(float(hit.get('attr_bv_average_overall_rating', {}).get('ar', 0)), 2)
                    item['MainImage'] = hit.get('media', [])
                    if item['MainImage']:
                        item['MainImage'] = item['MainImage'][0].get('url')
                    item['Offer'] = round(float(hit.get('gtm', {}).get('gtm-price')), 2)
                    item['RegularPrice'] = round(float(hit.get('gtm', {}).get('gtm-old-price')), 2)
                    if item['Offer'] == item['RegularPrice']:
                        item['Offer'] = 0

                    url = hit.get('url', {}).get('en')
                    item['URL'] = self.main_url + url

                    #item['page'] = page

                    item['BrandCode']= ''
                    item['ModelNumber']= ''
                    item['VendorCode']= vendor_code
                    catalogue_code = response.meta['catalogue_code']
                    # item['CategoryName'] = item['CategoryName'].strip()
                    category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                    item['CatalogueCode']= catalogue_code
                    item['CategoryCode']= category_code
                    
                    self.count+=1
                    yield scrapy.Request(url=self.review_api.format(item['SKU']), dont_filter=False, headers=self.headers, callback=self.parse_review, meta={
                        'item': item,
                })
                
                print("Category = {}, Total Products = {} on Page = {}".format(category, self.count, page))
                page = page + 1
                modified_body = copy.deepcopy(self.body)      
                format_body = modified_body["requests"][0]["params"].format(category_code_f, page)
                modified_body["requests"][0]["params"] = format_body
                body = json.dumps(modified_body)
                yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category':category, 'category_code_f': category_code_f, 'catalogue_code': catalogue_code, 'page':page})

    def parse_review(self, response):
        item = response.meta['item']
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