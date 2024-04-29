import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemCentrePoint
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import mysql.connector




class CentrePointSpider(Spider):
    name = 'centrepoint'
    allowed_domains = ['www.centrepointstores.com', '3hwowx4270-dsn.algolia.net']
    main_url = 'https://www.centrepointstores.com/ae/en'
    products_api = 'https://3hwowx4270-dsn.algolia.net/1/indexes/*/queries?X-Algolia-API-Key=4c4f62629d66d4e9463ddb94b9217afb&X-Algolia-Application-Id=3HWOWX4270&X-Algolia-Agent=Algolia%20for%20vanilla%20JavaScript%202.9.7'
   
    
    categories = {
                "Fashion": {
                        'Men Clothing': 'cpmen-clothing',
                        'Men Shoes': 'cpmen-footwear',
                        'Men Bags': 'cpmen-fashionaccessories-bagsandwallets',
                        'Men Accessories': 'cpmen-fashionaccessories',
                        'Men Shoes': 'cpmen-footwear-sportsshoes',
                        'Men Sportswear': 'cpmen-clothing-sportswearandactivewear',
                        'Men Clothing': 'cpmen-clothing-plussizeclothing',
                        'Men Perfumes': 'cpmen-perfumes',
                        'Women Clothing': 'cpwomen-clothing',
                        "Women Shoes": 'cpwomen-footwear',
                        "Women Accessories": 'cpwomen-fashionaccessories',
                        'Women Shoes': 'cpwomen-footwear-sportsshoes',
                        'Women Sportswear': 'cpwomen-clothing-sportswearandactivewear',
                        'Women Clothing': 'cpwomen-arabicclothing',
                        'Women Clothing': 'cpwomen-clothing-lingerie',
                        'Women Clothing': 'cpwomen-clothing-plussizeclothing'
                        },

                "Personal Care & Beauty": {
                    "Personal Care For Women": 'cpbeauty',
                },
                            
                "Baby & Kids": {
                                "Boys Clothing": 'cpbaby-clothing-boys',
                                "Girls Clothing": 'cpbaby-clothing-girls',
                                'Toys': 'cpbaby-toys',
                                "Girls Clothing": 'cpkids-clothing-girls',
                                'Girls Shoes': 'cpkids-footwear-girls',
                                'Girls Shoes': 'cpkids-footwear-girls-sportsshoes',
                                'Girls Sportswear': 'cpkids-clothing-girls-sportswear',
                                'Girls Accessories': 'cpkids-accessories-girls',    
                                "Boys Clothing": "cpkids-clothing-boys",
                                "Boys Shoes": "cpkids-footwear-boys",
                                'Boys Shoes': 'cpkids-footwear-boys-sportsshoes',
                                'Boys Sportswear': 'cpkids-clothing-boys-sportswear',
                                'Boys Accessories': 'cpkids-accessories-boys',
                                "Nursery": "cpkids-backtoschool",
                                'Feeding & Nursing': 'cpbaby-nursery',
                                'Strollers, Gear & Accessories': 'cpbaby-travelgear',
                                'Feeding & Nursing': 'cpbaby-feeding',
                                'Diapers, Bath & Skincare': 'cpbaby-diapersandwipes',
                                'Diapers, Bath & Skincare': 'cpbaby-bathandpottytraining',
                                'Safety Accessories': 'cpbaby-healthandsafety-safetyessentialsandhygiene',
                            },

                "Home": {
                            "Home Fragrance": 'cphomeandliving-homefragrance',
                            "Home Furniture": 'cphomeandliving-homefurniture',
                            "Home Dining": 'cphomeandliving-diningandserving',
                            "Home Furnishings": 'cphomeandliving-homefurnishings',
                            "Home Kitchen": 'cphomeandliving-kitchen',
                            "Home Decor and Lighting": 'cphomeandliving-homedecor',
                            "Home Bath": 'cphomeandliving-bathdecor'
                        },

                "Personal Care & Beauty": {
                            'Makeup & Accessories': 'cpbeauty-makeup',
                            'Fragrances & Perfumes': 'cpbeauty-fragrance',
                            'Personal Care For Women': 'cpbeauty-skincare',
                            'Personal Care For Women': 'cpbeauty-bathandbody',
                            'Personal Care For Women': 'cpbeauty-haircare',
                            'Personal Care For Women': 'cpbeauty-makeup-nails'
                            },

                "Sports Equipment": {
                            'Hiking & Outdoor': 'cpsports-allsports-campingandhiking',
                            'Tennis': 'cpsports-allsports-racketsports-tennis',
                            'Table Tennis': 'cpsports-allsports-racketsports-tabletennis',
                            'Badminton': 'cpsports-allsports-racketsports-badminton',
                            'Squash': 'cpsports-allsports-racketsports-squash',
                            'Swimming': 'cpsports-allsports-watersports-swimming',
                            'Fitness': 'cpsports-allsports-gym',
                            'Fitness': 'cpsports-allsports-homegym',
                            'Rugby & Football': 'cpsports-allsports-football',
                            'Volleyball': 'cpsports-allsports-volleyball',
                            "Basketball": 'cpsports-allsports-basketball',
                            'Fitness': 'cpsports-allsports-supports' 
                          },

                'Health & Medical': {
                            'Nutrition': 'cpsports-nutrition'
                        }
            
            }

                            

    headers = {'Content-Type': 'application/json'}
    
    
    body = {"requests":[{"indexName":"prod_uae_centrepoint_Product","params":"query=*&hitsPerPage=42&page={}&facets=*&facetFilters=%5B%22inStock%3A1%22%2C%22approvalStatus%3A1%22%2C%22allCategories%3A{}%22%2C%22badge.title.en%3A-LASTCHANCE%22%5D&getRankingInfo=1&clickAnalytics=true&attributesToHighlight=null&analyticsTags=%5B%22{}%22%2C%22en%22%2C%22Webmobile%22%5D&attributesToRetrieve=concept%2CmanufacturerName%2Curl%2C333WX493H%2C345WX345H%2C505WX316H%2C550WX550H%2C499WX739H%2Cbadge%2Cname%2Csummary%2CwasPrice%2Cprice%2CemployeePrice%2CshowMoreColor%2CproductType%2CchildDetail%2Csibiling%2CthumbnailImg%2CgallaryImages%2CisConceptDelivery%2CextProdType%2CreviewAvgRating%2CreferencesAvailable%2CitemType%2CbaseProductId%2CflashSaleData%2CcategoryName&numericFilters=price%20%3E%200.9&query=*&maxValuesPerFacet=500&tagFilters=%5B%5B%22babyshop%22%2C%22splash%22%2C%22lifestyle%22%2C%22shoemart%22%2C%22centrepoint%22%2C%22shoexpress%22%2C%22sportsone%22%2C%22sminternational%22%2C%22lipsy%22%2C%22dawsonsports%22%2C%22mumsygift%22%2C%22morecare%22%2C%22ramrod%22%2C%22styli%22%2C%22trucare%22%2C%22trucaredropship%22%2C%22rivoli%22%2C%22timehouse%22%2C%22sambox%22%2C%22desertbeat%22%2C%22cpelite%22%2C%22mhsglobal%22%2C%22mapyr%22%2C%22grandstores%22%2C%22wonderbrand%22%2C%22drnutrition%22%2C%22jumboelectronics%22%2C%22desertbeatconloc%22%2C%22grandbaby%22%2C%22emsons%22%2C%22leafcompany%22%2C%22areeneast%22%2C%22elpan%22%2C%22supremeimpex%22%2C%22topgear%22%2C%22kermaventures%22%2C%22aliusie%22%2C%22triibedistribution%22%2C%22jossette%22%2C%22miniandyou%22%2C%22klugtoys%22%2C%22vdtrading%22%2C%22petsmartae%22%2C%22ichigoglobal%22%2C%22thinkplay%22%2C%22simbadickie%22%2C%22toytriangl%22%2C%22babico%22%2C%22playsmart%22%2C%22jayceebrands%22%2C%22brandhub%22%2C%22emaxdropship%22%2C%22jumbodropship%22%2C%22western%22%2C%22andadorbabywear%22%2C%22pinkandblue%22%2C%22mummazone%22%2C%22apparelgroup%22%2C%22montreal%22%2C%22wetrade%22%2C%22antworktrading%22%2C%22gigimedical%22%2C%22greenfuture%22%2C%22clovia%22%2C%22geopartnering%22%2C%22aalamialmutnawa%22%2C%22coega%22%2C%22justshop%22%2C%22shopfils%22%2C%22otantik%22%2C%22lscottonhome%22%2C%22msbm%22%2C%22biggbrands%22%2C%22wizzotoys%22%2C%22haidarous%22%2C%22oxiwave%22%2C%22liwa%22%2C%22zarabi%22%2C%22selfoss%22%2C%22ddaniela%22%2C%22bsapparelgroup%22%2C%22bsliwa%22%2C%22alfuttaim%22%2C%22shiphilinternational%22%2C%22alkhayam%22%5D%5D"}]}

    #Just make page and category name dynamic in body

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100, 
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log'
    }
    page = 0
    count = 0

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
        for category, subcategories in self.categories.items():
            catalogue_code = self.get_catalogue_code(category)
            if catalogue_code:
                print("########################################", category)
                for subcategory, subcategory_code in subcategories.items():
                    modified_body = copy.deepcopy(self.body)
                    format_body = modified_body["requests"][0]["params"].format(self.page, subcategory_code, subcategory_code)
                    modified_body["requests"][0]["params"] = format_body
                    body = json.dumps(modified_body)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, callback=self.parse, meta={'category': category, 'subcategory': subcategory, 'subcategory_code': subcategory_code, 'page': self.page, 'catalogue_code': catalogue_code})

    
    def parse(self, response):
        item = ProductItemCentrePoint()
        category = response.meta['category']
        subcategory = response.meta['subcategory']
        subcategory_code = response.meta['subcategory_code']
        vendor_code = self.vendor_code
        print("Category: ", category)
        page = response.meta['page']
        data = json.loads(response.text)
        results = data.get('results', [])
        for result in results:
            hits = result.get('hits', [])
            if hits:
                for hit in hits:
                    item['ProductName'] = hit.get('name', {}).get('en')
                    item['CatalogueName'] = category
                    item['CategoryName'] = subcategory
                    item['RatingValue'] = hit.get('reviewAvgRating', {}).get('avgProductRating', 0)
                    item['RatingValue'] = round(float(item['RatingValue']), 2)
                    item['MainImage'] = hit.get('gallaryImages', [])[0]
                    item['Offer'] = hit.get('price')
                    item['Offer'] = round(float(item['Offer']), 2)
                    item['RegularPrice'] = hit.get('wasPrice', 0)
                    item['RegularPrice'] = round(float(item['RegularPrice']), 2)
                    url = next(iter(hit.get('url', {}).values()), "")
                    url = url.get('en', '')
                    item['URL'] = self.main_url + url
                    item['SKU'] = hit.get('objectID')
                    #item['page'] = page
                    item['BrandName'] = ''
                    item['BrandCode'] = ''
                    item['ModelNumber'] = ''
                    item['VendorCode'] = vendor_code
                    item['StockAvailability'] = 1
                    catalogue_code = response.meta['catalogue_code']
                    category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                    item['CatalogueCode'] = catalogue_code
                    item['CategoryCode'] = category_code
                    
                    self.count = self.count + 1
                    yield item
                
                print("Category = {}, Total Products = {} on Page = {}".format(category, self.count, page))
                page = page + 1
                modified_body = copy.deepcopy(self.body)      
                format_body = modified_body["requests"][0]["params"].format(page, subcategory_code, subcategory_code)
                modified_body["requests"][0]["params"] = format_body
                body = json.dumps(modified_body)
                yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category': category, 'subcategory': subcategory, 'subcategory_code': subcategory_code, 'page': page, 'catalogue_code': catalogue_code})