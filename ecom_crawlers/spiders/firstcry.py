import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemFirstCry
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import mysql.connector



class FirstCrySpider(Spider):
    name = 'firstcry'
    allowed_domains = ['www.firstcry.ae']
    #products_url = 'https://www.firstcry.ae/clothes-and-shoes/6/0/0?gender=boy,unisex&ref2=menu_dd_boy_viewall#sale=6&brandid=0&searchstring=brand@@@@1@0@20@@@@@@@@@@@@@@@@@@@@@&rating=&sort=Popularity&&vi=three&pmonths=&cgen=&skills=&measurement=&material=&Color=&Age=&gender=&ser=&premium=&fulfilment=&personalize=&PageNo=1&scrollPos=155&pview=&tc=13891'
    #products_api = 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisefilterproducts?pageno={}&pagesize=20&sortexpression=Popularity&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&rating=&offer=&catid={}&skills=&material=&measurement=&gender=&exclude=&p=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize='
    review_api = 'https://www.firstcry.ae/api/rating/getpdsizesquereviewdata'
    
    page = 1
    # sub_categories = {
    # 'Hair Bands': 224,
    # 'Finger Rings & Ear Rings': 225,
    # 'Hair Clips and Rubber': 228,
    # 'Handbags and Purses': 234,
    # 'Kids Jewellery': 226,
    # 'Kids Sunglasses': 237,
    # 'Kids Umbrellas': 377,
    # 'Make Up & Cosmetics': 227,
    # 'Ties, Belts and Suspenders': 245,
    # 'Watches': 275
    # }

    categories = {
                    'Fashion':  {
                                    'Men Clothing': 'https://www.firstcry.ae/api/searchresult.svc/getsearchresultproductsfilters?pageno={}&pagesize=20&sortexpression=Popularity&onsale=6&searchstring=brand&subcatid=168,165,164,269,243,166,220,267,276,295,221,26&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&masterbrand=0&sorting=&rating=&offer=&skills=&material=&measurement=&gender=both,male&exclude=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize=',
                                    'Women Clothing': 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisefilterproducts?pageno={}&pagesize=20&sortexpression=Popularity&subcatid=168,165,164,269,243,166,220,267,276,295,221,26&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&rating=&offer=&catid=6&skills=&material=&measurement=&gender=both,female&exclude=&p=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize=',
                                    'Men Shoes': 'https://www.firstcry.ae/api/searchresult.svc/getsearchresultproductsfilters?pageno={}&pagesize=20&sortexpression=Popularity&onsale=6&searchstring=brand&subcatid=170&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&masterbrand=0&sorting=&rating=&offer=&skills=&material=&measurement=&gender=both,male&exclude=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize=',
                                    'Women Shoes': 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisefilterproducts?pageno=1&pagesize=20&sortexpression=Popularity&subcatid=170&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&rating=&offer=&catid=6&skills=&material=&measurement=&gender=both,female&exclude=&p=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize='
                                },

                    'Baby & Kids': {
                                'Toys': 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisefilterproducts?pageno={}&pagesize=20&sortexpression=Popularity&subcatid=&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&rating=&offer=&catid=5&skills=&material=&measurement=&gender=&exclude=&p=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize=',
                                'Strollers, Gear & Accessories': 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisefilterproducts?pageno={}&pagesize=20&sortexpression=Popularity&subcatid=&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&rating=&offer=&catid=7&skills=&material=&measurement=&gender=&exclude=&p=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize=',
                                'Nursery': 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisefilterproducts?pageno={}&pagesize=20&sortexpression=Popularity&subcatid=&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&rating=&offer=&catid=8&skills=&material=&measurement=&gender=&exclude=&p=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize=',
                                'Diapers, Bath & Skincare': 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisefilterproducts?pageno={}&pagesize=20&sortexpression=Popularity&subcatid=&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&rating=&offer=&catid=1&skills=&material=&measurement=&gender=&exclude=&p=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize=',
                                'Diapers, Bath & Skincare': 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisefilterproducts?pageno={}&pagesize=20&sortexpression=bestseller&subcatid=&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&rating=&offer=&catid=3&skills=&material=&measurement=&gender=&exclude=&p=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize=',
                                'Feeding & Nursing': 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisefilterproducts?pageno={}&pagesize=20&sortexpression=bestseller&subcatid=&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&rating=&offer=&catid=2&skills=&material=&measurement=&gender=&exclude=&p=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize=',
                                },

                        'Office Supplies':   {
                                     'Stationary': 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisefilterproducts?pageno={}&pagesize=20&sortexpression=Popularity&subcatid=&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&rating=&offer=&catid=10&skills=&material=&measurement=&gender=&exclude=&p=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize=',       
                                    },
                        
                        'Home Appliances':     {
                                      'Home Appliances Accessories': 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisefilterproducts?pageno={}&pagesize=20&sortexpression=Popularity&subcatid=&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&rating=&offer=&catid=229&skills=&material=&measurement=&gender=&exclude=&p=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize='
                                    },

                        'Beauty':   {
                                      'Womens Beauty and Personal Care': 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisefilterproducts?pageno={}&pagesize=20&sortexpression=Popularity&subcatid=&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&rating=&offer=&catid=78&skills=&material=&measurement=&gender=&exclude=&p=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize=',
                                      'Makeup': 'https://www.firstcry.ae/api/searchresult.svc/getsearchresultproductsfilters?pageno={}&pagesize=20&sortexpression=bestseller&onsale=15&searchstring=brand&subcatid=&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&masterbrand=0&sorting=&rating=&offer=&skills=&material=&measurement=&gender=&exclude=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize='
                                    },
                        
                        'Safety':   {
                                      'Health and Safety': 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisefilterproducts?pageno={}&pagesize=20&sortexpression=Popularity&subcatid=&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&rating=&offer=&catid=4&skills=&material=&measurement=&gender=&exclude=&p=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize=',
                                    },

                        'Moms':     {
                                      'Moms and Maternity': 'https://www.firstcry.ae/api/searchresult.svc/getsearchresultproductspaging?pageno={}&pagesize=20&sortexpression=Popularity&onsale=21&searchstring=brand&subcatid=&brandid=&price=&age=&color=&optionalfilter=&outofstock=1&type1=&type2=&type3=&type4=&type5=&type6=&type7=&type8=&type9=&type10=&type11=&type12=&type13=&type14=&type15=&combo=&discount=&searchwithincat=&productidqstr=&searchrank=&pmonths=&cgen=&priceqstr=&discountqstr=&sorting=&masterbrand=0&rating=&offer=&skills=&material=&measurement=&gender=&exclude=&premium=&ln=en&pcode=U000201&fulfilment=&cnid=uae&personalize='
                                    }

    }

    headers = {'Content-Type': 'application/json'}
    body = {"pid": None, "auth": "null", "cnid": "uae", "ln" : "en"}
    

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
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
        for main_cat, sub_cats in self.categories.items():
            catalogue_code = self.get_catalogue_code(main_cat)
            if catalogue_code:
                for sub_cat_name, sub_cat_url in sub_cats.items():
                    page = self.page
                    yield scrapy.Request(url=sub_cat_url.format(page), callback=self.parse, meta={"main_category": main_cat, "sub_category": sub_cat_name, "cat_url": sub_cat_url, "page": page, 'catalogue_code': catalogue_code})


    
    def parse(self, response):
        main_category = response.meta['main_category']
        sub_category = response.meta['sub_category']
        catalogue_code = response.meta['catalogue_code']
        print("Category: ", sub_category)
        page = response.meta['page']
        cat_url = response.meta['cat_url']
        vendor_code = self.vendor_code
        data = json.loads(response.text)
        product_response_str = data.get('ProductResponse', {})
        product_response = json.loads(product_response_str)
        products_list = product_response.get('Products', [])

        if len(products_list) > 0:
            print("########################PAGE {}############################".format(page))
            for product in product_response['Products']:
                pid = product.get('PId')
                name = product.get('PNm')
                brand = product.get('BNm')
                age_from = product.get('AgeF')
                age_to = product.get('AgeT')
                age = str(age_from) + ' To ' + str(age_to) 
                size = product.get('size')
                rating = product.get('rating')
                price = product.get('discprice')
                self.body['pid'] = pid
                yield scrapy.Request(url=self.review_api, method='POST', headers=self.headers, body=json.dumps(self.body), callback=self.parse_review, 
                                     meta={'pid': pid,
                                           'name': name,
                                           'brand': brand,
                                           'age': age,
                                           'size': size,
                                           'rating': rating,
                                           'price': price,
                                           'main_category': main_category,
                                           'sub_category': sub_category,
                                           'vendor_code': vendor_code,
                                           'catalogue_code': catalogue_code,
                                           'page': page})
            page = page + 1
            yield scrapy.Request(url=cat_url.format(page), meta={"main_category": main_category, "sub_category": sub_category, "cat_url": cat_url, "page": page, 'catalogue_code': catalogue_code})


    def parse_review(self, response):
        item = ProductItemFirstCry()
        data = json.loads(response.text)
        item_reviews = []
        customer_review_list = data.get('CustomerReviewList', [])
    
        item['SKU'] = response.meta['pid']
        item['ProductName'] = response.meta['name']
        item['BrandName'] = response.meta['brand']
        age = response.meta['age']
        size = response.meta['size']
        item['RatingValue'] = response.meta['rating']
        item['RatingValue'] = round(float(item['RatingValue']), 2)
        item['RegularPrice'] = response.meta['price']
        item['RegularPrice'] = round(float(item['RegularPrice']), 2)
        item['Offer'] = 0
        item['CatalogueName'] = response.meta['main_category']
        item['CategoryName'] = response.meta['sub_category']
        page = response.meta['page']
        item['VendorCode'] = response.meta['vendor_code']
        item['StockAvailability'] = 1
        item['ModelNumber'] = ''
        item['BrandCode'] = ''
        item['URL'] = ''
        item['MainImage'] = ''
        catalogue_code = response.meta['catalogue_code']
        category_code = self.get_category_code(item['CategoryName'], catalogue_code)
        item['CatalogueCode'] = catalogue_code
        item['CategoryCode'] = category_code

        if customer_review_list:
            for review in customer_review_list:
                comment = review.get('reviewdata', '')
                source = ''
                comment_date = review.get('createdate', '')
                comment_date = datetime.strptime(comment_date, "%m/%d/%Y %I:%M:%S %p")
                comment_date = comment_date.strftime("%Y-%m-%d")
                rating = round(float(review.get('rating')), 2)
                max_rating = round(5, 2)

                
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
