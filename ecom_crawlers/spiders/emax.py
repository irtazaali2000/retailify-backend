import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemEmax
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import os
import psycopg2
from copy import deepcopy


class EmaxSpider(Spider):
    name = 'emax'
    allowed_domains = ['uae.emaxme.com', '3hwowx4270-dsn.algolia.net']
    main_url = 'https://uae.emaxme.com'
    products_api = 'https://3hwowx4270-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.22.1)%3B%20Browser'
    model_no_api = 'https://uae.emaxme.com/api/catalog-browse/browse/products?productIds={}'
    headers = {'Content-Type': 'application/json', 'X-Algolia-Api-Key': '4c4f62629d66d4e9463ddb94b9217afb', 'X-Algolia-Application-Id': '3HWOWX4270'}
    headers_product = {
        "authority": "uae.emaxme.com",
        "method": "GET",
        "scheme": "https",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en",
        "cache-control": "no-cache",
        "cookie": "USER_DATA=%7B%22attributes%22%3A%5B%5D%2C%22subscribedToOldSdk%22%3Afalse%2C%22deviceUuid%22%3A%2231fde329-1745-4161-baf2-f8bacbd8883b%22%2C%22deviceAdded%22%3Atrue%7D; concept=emax; lang=en; country=ae; _app_deviceId=user_172596406440120416; mt.v=2.291381695.1725964065667; _traceId=; _fw_crm_v=0fa73e11-e1de-4f66-daac-9ee6599b2a30; _ga=GA1.1.253441804.1725964073; _ga=GA1.3.253441804.1725964073; _fbp=fb.1.1725964074356.548979787775442443; _ALGOLIA=anonymous-36bb5494-7206-4816-a7bc-061f2b91e614; moe_uuid=31fde329-1745-4161-baf2-f8bacbd8883b; isLoggedIn=false; _gid=GA1.3.482590454.1726648263; OPT_IN_SHOWN_TIME=1726648265351; SOFT_ASK_STATUS=%7B%22actualValue%22%3A%22dismissed%22%2C%22MOE_DATA_TYPE%22%3A%22string%22%7D; _gcl_au=1.1.1327199082.1725964072.1451556616.1726667311.1726667311; JSESSIONID=D29EC8E4FEA5799B33B95E7FB7F1F967; selectedDeptae=mobile; preSelectedDeptae=mobile; BLSR=eyJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJicm9hZGxlYWYtYXV0aGVudGljYXRpb24iLCJzdWIiOiJCTFNSIiwiYXVkIjoiYnJvYWRsZWFmLWF1dGhlbnRpY2F0aW9uIiwicmVkaXJlY3RVcmwiOiJhSFIwY0hNNkx5OTFZV1V1WlcxaGVHMWxMbU52YlM5aGRYUm9MMjloZFhSb0wyRjFkR2h2Y21sNlpUOWpiR2xsYm5SZmFXUTlaVzFoZUY5aFpTWndjbTl0Y0hROWJtOXVaU1p5WldScGNtVmpkRjkxY21rOWFIUjBjSE1sTTBFbE1rWWxNa1oxWVdVdVpXMWhlRzFsTG1OdmJTVXlSbk5wYkdWdWRDMWpZV3hzWW1GamF5NW9kRzFzSm5KbGMzQnZibk5sWDNSNWNHVTlZMjlrWlNaelkyOXdaVDFWVTBWU0pUSXdRMVZUVkU5TlJWSmZWVk5GVWlVeU1FbE9Wa1ZPVkU5U1dWOVRWVTFOUVZKWkpuTjBZWFJsUFZKRVJrZFZSMXBSWld0NE5FNXVZM3BTZW14MlVURnNVazlGTlVsWGJXdzFaRVV4ZWxacWJIUlpiWFJDVTIwMVVGUnNXbTVhYW1oVFpGRWxNMFFsTTBRPSIsInJlcXVlc3RVcmwiOiJhSFIwY0hNNkx5OTFZV1V1WlcxaGVHMWxMbU52YlM5aGRYUm9MMjloZFhSb0wyRjFkR2h2Y21sNlpRPT0ifQ.Qroq15Q3Cl4ffE-h2BiyNiVnJnkJO36IBy00qS15V6taL0R0t6PLjveZgkn8PaLElpqK1ox0MwEMMgd_M2R9HUq8oEFdgyHMVk0ckTnIaM92DRIxc0BIrXtdtNwD_Llkk8kSEkTLtKtpMP3GI6Z8U3zMJDIcLDFq58v32TU8EWWbFgtw_4SOYVaY7LrwMps-Eki6dgu-bAeA7sJv_frfBHMPPayNM5D0wXuajaM0LUQ6pnzG9Mk9XzLZjDqC-57DEioAw5Qr0gZJYDjxWZA1Rzdsel0NU8OeiSCACDyoEiWBUIpkahomqwNmQxO5IB3mceCOK6Z0AaZ20pfaUIZ7Bw; first_session=%7B%22visits%22%3A27%2C%22start%22%3A1725964072628%2C%22last_visit%22%3A1726730283663%2C%22url%22%3A%22https%3A%2F%2Fuae.emaxme.com%2F%3Fsrsltid%3DAfmBOoqJRR4x-VahgozLJtACVCKVKxg7T_nb2PlP-OukHbxEx7rujbeL%22%2C%22path%22%3A%22%2F%22%2C%22referrer%22%3A%22https%3A%2F%2Fuae.emaxme.com%2F%3Fsrsltid%3DAfmBOoqJRR4x-VahgozLJtACVCKVKxg7T_nb2PlP-OukHbxEx7rujbeL%26__cf_chl_tk%3D4dlWiDbvT_uI_vzAYw_T.BYthp0jG1OjpOPH8laT2r0-1725964054-0.0.1.1-8894%22%2C%22referrer_info%22%3A%7B%22host%22%3A%22uae.emaxme.com%22%2C%22path%22%3A%22%2F%22%2C%22protocol%22%3A%22https%3A%22%2C%22port%22%3A80%2C%22search%22%3A%22%3Fsrsltid%3DAfmBOoqJRR4x-VahgozLJtACVCKVKxg7T_nb2PlP-OukHbxEx7rujbeL%26__cf_chl_tk%3D4dlWiDbvT_uI_vzAYw_T.BYthp0jG1OjpOPH8laT2r0-1725964054-0.0.1.1-8894%22%2C%22query%22%3A%7B%22srsltid%22%3A%22AfmBOoqJRR4x-VahgozLJtACVCKVKxg7T_nb2PlP-OukHbxEx7rujbeL%22%2C%22__cf_chl_tk%22%3A%224dlWiDbvT_uI_vzAYw_T.BYthp0jG1OjpOPH8laT2r0-1725964054-0.0.1.1-8894%22%7D%7D%2C%22search%22%3A%7B%22engine%22%3Anull%2C%22query%22%3Anull%7D%2C%22prev_visit%22%3A1726730250656%2C%22time_since_last_visit%22%3A33007%2C%22version%22%3A0.4%7D; cto_bundle=Enfy5V9DNmF1SktlbExJbDR1bk5VTmJ0MUQ2YkMzV1p6RiUyRnFBVTZnVXB2TFJucHBVWm0yaiUyRnBMRzBNUVFFNmZibzFHUUY4WldxaXZ6R3o5am83Wk9zRkQwYnJacFAxdU0zVmdpJTJCVGpJRTk1Q3JPTWpCMngzYkpKbU5CTUtyYUF6czhnczl0TGRFUDFRUjE1RiUyRlc3cVo3REw5RUZMTEw1UlRPdnIlMkZ2bCUyQjY5RmdGUUd0MmRpSDhxVmxzSlI5a0I1SnB0QTVJRyUyQktOem11VlpjUTBrazQwaXpFYmclM0QlM0Q; _ga_WW9R6WB2SB=GS1.1.1726730219.13.1.1726730290.51.0.0; SESSION=%7B%22sessionKey%22%3A%22b1d662bc-f248-40e3-98cc-16f374f90f2c%22%2C%22sessionStartTime%22%3A%222024-09-19T07%3A18%3A11.745Z%22%2C%22sessionMaxTime%22%3A1800%2C%22customIdentifiersToTrack%22%3A%5B%5D%2C%22sessionExpiryTime%22%3A1726732091823%2C%22numberOfSessions%22%3A21%7D; ADRUM=s=1726733648784&r=https%3A%2F%2Fuae.emaxme.com%2Fbuy-samsung-galaxy-s24-ultra-12gb-256gb-titanium-black-5g-p-01HM6DBTAQBKBR0ZZJGHAZ1SYG-Titanium%2520Black-12GB%2520256GB.html; cf_clearance=LnmyV65KiJsXBA8qP259H2ckexEsvHGZbl5.I.zYxBg-1726733659-1.2.1.1-9H98lo5DTjTvI1apycxYLR8ijVb9H2TYWqYggdEO24l4rq4.T629q2Bo2Rd3zaH3oXVbrVtslmVxgiCKmlP5EqyeUI59BGpmyS2Or0itwjnr1TflkJCB9aRqVzCrWSipez7PVUCqPP4fHMln.DokY1hKcMFk5gZGWG7wz_a8rwdfV7AUEvXhh9ExIknLpk35pLiz7.W7zkHpTrJBE2vHtpH13qnblgTwTuSO9nnrwdjtOQtbYiMDM2MzrcfmjgGutQ.9TL6AffRju9V3vEA5c.8NeVXjAQtsJvQXdNhG4oG8Y6XHTMZrqmcD450CZMz0cDgAY.eqeMMzsHEfg1JvVKsGvYhhffUq1nMnXLdNnaTA_CasW3StN9RtJWzobiseq.WS56oieebmYUGT_mLfyA1QTjArw4zoAI1yZY8vFiIeYqNY.ZS.yEr02EjKRm5CxvaXx_aGlHnsLNtyNd3Vlg; __cf_bm=B11b8HR6fGkIiF8YBvhKKG6i_Faui4cdlRcJ1MBsOOM-1726733672-1.0.1.1-mpjVwYUxQ46SGm8bytX7H9jhPfzDrE5Tl9aTIfMlN8MMV0nBkGmWAaXkPMVrOaBYShoS8ySj764lR.TjWWrUqg",
        "pragma": "no-cache",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "Android",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
        "referer": "https://uae.emaxme.com",
    }


    
    body = {"requests":[{"indexName":"prod_uae_emax_product","query":"*","params":"facets=*&page={}&hitsPerPage=48&attributesToRetrieve=*&attributesToHighlight=%5B%22name%22%5D&maxValuesPerFacet=1000&getRankingInfo=true&facetFilters=%5B%22inStock%3A1%22%2C%22approvalStatus%3A1%22%2C%22allCategories%3A{}%22%5D&numericFilters=%5B%22price%20%3E%200%22%5D&clickAnalytics=true"}]}
    #Just make page and category name dynamic in body

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter',
        #'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }
    page = 0
    count = 0
    

    # categories = {
    #             # 'Mobiles Tablets & Wearables'
    #             'Electronics': {
    #                                         'Mobile Phones': 'mobile',
    #                                         #'Mobile Accessories': 'mobileaccessories',
    #                                         #'Tablets & Ereaders': 'laptoptabletandcomputeraccessories-tablets'
    #                                         },
    #             # 'Computers'
    #             'Electronics': {
    #                             'Laptops': 'laptoptabletandcomputeraccessories-laptops',
    #                             #'Computers Accessories': 'laptoptabletandcomputeraccessories-computeraccessories'
                                
    #                         },

    #             # Video, Lcd & Oled
    #             'Electronics': {
    #                         'Tv': 'televisionandaudio-television',
    #             },

    #             # Audio, Headphones & Music Players
    #             'Electronics': {
    #                 'Audio Accessories': 'televisionandaudio-audio'
    #             },

    #             # 'Home Appliances': {
    #             #     'Home Appliances Accessories': 'homeappliances',
    #             #     'Kitchen Appliances': 'kitchenappliances'
    #             # },

    #             # 'Personal Care & Beauty': {
    #             #     'Makeup & Accessories': 'personalcare'
    #             # },

    #             # 'Video Games & Consoles': {
    #             #     'Games Accessories': 'gamingandgamingaccessories'
    #             # },

    #             # 'Camcorders & Cameras
    #             'Electronics': {
    #                 'Camera Accessories': 'photographylensesanddrones'
    #                 },

    #             # 'Musical Instruments': {
    #             #     'Keyboards & Midi Instruments': 'musicalinstruments'
    #             # }
                    
    #     }

    categories = {

            'Electronics': {
                'Mobile Phones': 'mobile',
                'Laptops': 'laptoptabletandcomputeraccessories-laptops',
                'Tv': 'televisionandaudio-television',
                'Audio Accessories': 'televisionandaudio-audio',
                'Camera Accessories': 'photographylensesanddrones'
                    },
     
                    
        }
    

                
    
    conn = psycopg2.connect(
        dbname="retailifydb3",
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    def __init__(self, reviews='False', short_scraper="False", *args, **kwargs):
        super().__init__()

        # Set up the log directory and file path
        log_dir = 'scrapy-logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)  # Create the directory if it doesn't exist

        log_file = f'{log_dir}/{self.name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log'
        self.custom_settings['LOG_FILE'] = log_file

        self.reviews = reviews.lower() == 'true'
        self.short_scraper = short_scraper.lower() == 'true'
        catalogue_url = CATALOGUE_URL_T.format(self.name, self.short_scraper)
        categories_url = "{}{}".format(HOST, catalogue_url)
        raw_res = requests.get(categories_url).json()
    #     self.categories = raw_res.get('data', [])
        self.vendor_code = raw_res.get('VendorCode')


    def get_catalogue_code(self, catalogue_name):
        # Attempt to retrieve the catalog code and name from the database
        query_select = 'SELECT "CatalogueCode", "CatalogueName" FROM product_catalogue WHERE "CatalogueName" = %s'
        self.cursor.execute(query_select, (catalogue_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the catalog code exists, check if the name needs to be updated
            if result[1] != catalogue_name:
                update_query = 'UPDATE product_catalogue SET "CatalogueName" = %s WHERE "CatalogueCode" = %s'
                self.cursor.execute(update_query, (catalogue_name, result[0]))
                self.conn.commit()  # Commit the transaction
                
            return result[0]
        else:
            # If the catalog code doesn't exist, insert it into the database
            insert_query = 'INSERT INTO product_catalogue ("CatalogueName") VALUES (%s) RETURNING "CatalogueCode"'
            self.cursor.execute(insert_query, (catalogue_name,))
            self.conn.commit()  # Commit the transaction

            # # Retrieve the newly inserted category code and name
            # self.cursor.execute(query_select, (catalogue_name,))
            # result = self.cursor.fetchone()
            # return result[0] if result else None
        
            result = self.cursor.fetchone()
            return result[0] if result else None


    
    def get_category_code(self, category_name, catalogue_code):
        # Attempt to retrieve the category code and name from the database
        query_select = 'SELECT "CategoryCode", "CategoryName" FROM product_category WHERE "CategoryName" = %s'
        self.cursor.execute(query_select, (category_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the category code exists, check if the name needs to be updated
            if result[1] != category_name:
                update_query = 'UPDATE product_category SET "CategoryName" = %s WHERE "CategoryCode" = %s'
                self.cursor.execute(update_query, (category_name, result[0]))
                self.conn.commit()  # Commit the transaction
            
            return result[0]
        else:
            # If the category code doesn't exist, insert it into the database
            insert_query = 'INSERT INTO product_category ("CategoryName", "CatalogueCode_id") VALUES (%s, %s) RETURNING "CategoryCode"'
            self.cursor.execute(insert_query, (category_name, catalogue_code))
            self.conn.commit()  # Commit the transaction
            
            # # Retrieve the newly inserted category code and name
            # self.cursor.execute(query_select, (category_name,))
            # result = self.cursor.fetchone()
            # return result[0] if result else None
            result = self.cursor.fetchone()
            return result[0] if result else None

    
    def start_requests(self):
        for main_category, subcategories in self.categories.items():
            catalogue_code = self.get_catalogue_code(main_category)
            if catalogue_code:
                for sub_category, sub_category_code in subcategories.items():
                    modified_body = copy.deepcopy(self.body)
                    format_body = modified_body["requests"][0]["params"].format(self.page, sub_category_code)
                    modified_body["requests"][0]["params"] = format_body
                    body = json.dumps(modified_body)
                    
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers,
                                        body=body, callback=self.parse,
                                        meta={'category': main_category, 'sub_category': sub_category, 'category_code_f': sub_category_code, 'page': self.page, 'vendor_code': self.vendor_code, 'catalogue_code': catalogue_code})

        
    
    def parse(self, response):
        item = ProductItemEmax()
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        category_code_f = response.meta['category_code_f']
        vendor_code = response.meta['vendor_code']
        print("Category: ", category)
        page = response.meta['page']
        data = json.loads(response.text)
        results = data.get('results', [])
        for result in results:
            hits = result.get('hits', [])
            if hits:
                #self.count = 0
                for hit in hits:
                    item['ProductName'] = hit.get('name', {}).get('en')
                    #manufacturer_name = hit.get('manufacturerName', '')
                    #if isinstance(manufacturer_name, str):
                     #   item['manufacturer_name'] = manufacturer_name
                    #else:
                     #   item['manufacturer_name'] = ''
                    
                    item['StockAvailability'] = hit.get('inStock')
                    item['BrandName'] = hit.get('brand', '')
                    item['BrandCode'] = hit.get('brandId', '')
                    #item['product_id'] = hit.get('productId')
                    item['SKU'] = hit.get('sku')
                    # item['Offer'] = hit.get('price')
                    # item['Offer'] = round(float(item['Offer']), 2)
                    # item['RegularPrice'] = hit.get('wasPrice', 0)
                    # item['RegularPrice'] = round(float(item['RegularPrice']), 2)

                    # if item['RegularPrice'] == item['Offer']:
                    #     item['Offer'] = 0

                    item['MyPrice'] = hit.get('price')
                    item['MyPrice'] = round(float(item['MyPrice']), 2)
                    item['Cost'] = hit.get('wasPrice', 0)
                    item['Cost'] = round(float(item['Cost']), 2)

                    if item['Cost'] == item['MyPrice']:
                        item['MyPrice'] = 0

                    img = hit.get('galleryImages', [])
                    if img:
                        item['MainImage'] = img[0].get('url', '')
                    else:
                        item['MainImage'] = ''
                    #item['color'] = hit.get('color', '')
                    #item['description'] = hit.get('description', {}).get('en', '')
                    url = hit.get('uri')
                    url = url.strip()
                    url = url.replace(" ", "%20")
                    item['URL'] = self.main_url + url
                    #item['percentage_discount'] = hit.get('percentageDiscount', 0)
                    item['CatalogueName'] = category
                    #item['CategoryName'] = hit.get('allCategories', [])[-1]
                    item['CategoryName'] = sub_category
                    #item['page'] = page
                    item['RatingValue'] = 0
                    # item['ModelNumber'] = ''
                    item['Currency'] = 'AED'
                    item['About'] = hit.get('description', {}).get('en')
                    item['Market'] = 'UAE'
                    #item['VendorCode'] = vendor_code
                    catalogue_code = response.meta['catalogue_code']
                    category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                    item['CatalogueCode']= catalogue_code
                    item['CategoryCode']= category_code
                    product_id = hit.get('productId')
                    uri = hit.get('uri')
                    color = hit.get('productOptions', {}).get('Color')
                    internal_memory =  hit.get('productOptions', {}).get('Capacity')
                    item['Color'] = color
                    item['InternalMemory'] = internal_memory

                    self.count+=1
                    # yield item

                    yield scrapy.Request(url=self.model_no_api.format(product_id), headers=self.headers_product, callback=self.parse_description, meta={'item': deepcopy(item), 'uri': uri})
                print("Category = {}, Total Products = {} on Page = {}".format(category, self.count, page))
                #Next Page

                page = page + 1
                modified_body = copy.deepcopy(self.body)      
                format_body = modified_body["requests"][0]["params"].format(page, category_code_f)
                modified_body["requests"][0]["params"] = format_body
                body = json.dumps(modified_body)
                #print(body)
                yield scrapy.Request(url=self.products_api, method='POST', callback=self.parse, headers=self.headers, body=body, meta={'category':category, 'sub_category': sub_category, 'category_code_f': category_code_f, 'page': page, 'vendor_code': vendor_code, 'catalogue_code': catalogue_code})


    def parse_description(self, response):
        item = response.meta['item']
        uri = response.meta['uri']
        data = json.load(response.text)
        products = data.get('products', [])
        for product in products:
            uri_from_response = product.get('uri')
            if uri_from_response == uri:
                externalId = product.get('externalId')
                item['ModelNumber'] = externalId
                break
        # model_number = response.xpath('//li[div[normalize-space(text())="Model No."]]/div[2]/text()').get()
        # color = response.xpath('//li[div[normalize-space(text())="Color"]]/div[2]/text()').get()
        # internal_memory = response.xpath('//li[div[normalize-space(text())="Capacity"]]/div[2]/text()').get()

        # item['Color'] = color
        # item['InternalMemory'] = internal_memory
        
        yield item