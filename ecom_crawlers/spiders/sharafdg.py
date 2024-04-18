import re
import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemSharafDG
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import mysql.connector



class SharafDGSpider(Spider):
    name = 'sharafdg'
    allowed_domains = ['uae.sharafdg.com', '9khjlg93j1-dsn.algolia.net', 'js.testfreaks.com', 'd1le22hyhj2ui8.cloudfront.net']
    #main_url = 'https://www.lifepharmacy.com/'
    products_api = 'https://9khjlg93j1-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.24.9%3BJS%20Helper%202.23.2&x-algolia-application-id=9KHJLG93J1&x-algolia-api-key=e81d5b30a712bb28f0f1d2a52fc92dd0'
    review_api_1 = 'https://d1le22hyhj2ui8.cloudfront.net/badge/sharafdg.com/reviews.json?key={}'
    review_api_2 = 'https://js.testfreaks.com/badge/sharafdg.com/reviews.json?pid={}&type=user'
    
    headers = {
               'Content-Type': 'application/json',
               'Referer': 'https://uae.sharafdg.com/'
                }
    
    body = {"requests":[{"indexName":"products_index","params":"query=&hitsPerPage=48&maxValuesPerFacet=20&page={}&attributesToRetrieve=permalink%2Cpermalink_ar%2Cpost_id%2Cpost_title%2Cpost_title_ar%2Cmain_sku%2Ctaxonomies.taxonomies_hierarchical.product_cat%2Ctaxonomies_ar.product_cat%2Ctaxonomies.product_brand%2Ctaxonomies_ar.product_brand%2Cdiscount%2Cdiscount_val%2Cimages%2Cprice%2Csku%2Cpromotion_offer_json%2Cregular_price%2Csale_price%2Cin_stock%2Ctags%2Crating_reviews%2Ctags_ar&attributesToHighlight=post_title%2Cpost_title_ar&getRankingInfo=1&filters=post_status%3Apublish%20AND%20price%3E0%20AND%20archive%3A0%20AND%20in_stock%3A1%20%20AND%20taxonomies.erp_ver%3A2&clickAnalytics=true&facets=%5B%22tags.title%22%2C%22taxonomies.attr.Brand%22%2C%22inventory.store_availability%22%2C%22price%22%2C%22rating_reviews.rating%22%2C%22promotion_offer_json.seller_code%22%2C%22taxonomies.ED_Seller%22%2C%22promotion_offer_json.fulfilled_by%22%2C%22taxonomies.attr.Processor%22%2C%22taxonomies.attr.Screen%20Size%22%2C%22taxonomies.attr.Internal%20Memory%22%2C%22taxonomies.attr.Type%22%2C%22taxonomies.attr.Storage%20Size%22%2C%22taxonomies.attr.RAM%22%2C%22taxonomies.attr.Graphics%20Card%22%2C%22taxonomies.attr.Color%22%2C%22taxonomies.attr.OS%22%2C%22taxonomies.attr.Size%22%2C%22taxonomies.attr.Megapixel%22%2C%22taxonomies.attr.Capacity%22%2C%22taxonomies.attr.Loading%20Type%22%2C%22taxonomies.attr.Tonnage%22%2C%22taxonomies.attr.Compressor%20Type%22%2C%22taxonomies.attr.Star%20Rating%22%2C%22taxonomies.attr.Energy%20input%22%2C%22taxonomies.attr.Water%20Consumption%22%2C%22taxonomies.attr.Control%20Type%22%2C%22taxonomies.attr.Number%20of%20Channels%22%2C%22taxonomies.attr.Audio%20Output%22%2C%22taxonomies.attr.No%20of%20Burners%2FHobs%22%2C%22taxonomies.attr.HDMI%22%2C%22taxonomies.attr.Total%20Capacity%22%2C%22taxonomies.attr.Number%20of%20Doors%22%2C%22taxonomies.attr.Watches%20For%22%2C%22taxonomies.attr.Display%20Type%22%2C%22taxonomies.attr.Water%20Resistant%20Depth%20(m)%22%2C%22taxonomies.attr.Power%20Source%22%2C%22taxonomies.attr.Net%20Content%22%2C%22taxonomies.attr.Target%20Group%22%2C%22taxonomies.attr.Fragrance%20Type%22%2C%22taxonomies.attr.Noise%20Cancellation%20Headphone%22%2C%22taxonomies.attr.Built-in%20%2F%20Free-standing%22%2C%22taxonomies.attr.Built%20In%20%2F%20Free%20Standing%22%2C%22taxonomies.attr.Mode%22%2C%22taxonomies.attr.Series%22%2C%22taxonomies.attr.PEGI%2FESRB%22%2C%22taxonomies.attr.Lens%20Color%22%2C%22taxonomies.attr.Lens%20Type%22%2C%22taxonomies.attr.Frame%20Material%22%2C%22taxonomies.attr.Frame%20Shape%22%2C%22taxonomies.attr.Focal%20Length%20Range%22%2C%22taxonomies.attr.Aperture%20Range%22%2C%22taxonomies.attr.Filter%20Thread%22%2C%22taxonomies.attr.Effective%20Megapixel%22%2C%22taxonomies.attr.Resolution%22%2C%22taxonomies.attr.Aspect%20Ratio%22%2C%22taxonomies.attr.Functions%22%2C%22taxonomies.attr.Print%20Technology%22%2C%22taxonomies.attr.Scanning%20speed%20(color)%22%2C%22taxonomies.attr.Supported%20Memory%20Type%22%2C%22taxonomies.attr.Seating%20Capacity%22%2C%22taxonomies.attr.Unit%20Components%20Count%22%2C%22taxonomies.attr.Battery%20Capacity%22%2C%22taxonomies.attr.USB%20Output%22%2C%22taxonomies.attr.Unit%20Component%22%2C%22taxonomies.attr.Toys%20Type%22%2C%22taxonomies.attr.Fitness%20Equipments%20Type%22%2C%22taxonomies.attr.Miscellaneous%20Type%22%2C%22taxonomies.attr.Cookware%20Type%22%2C%22taxonomies.attr.Outdoor%20Products%20Type%22%2C%22taxonomies.attr.Tools%20Type%22%2C%22taxonomies.attr.Ideal%20For%22%2C%22taxonomies.attr.Age%20Group%22%2C%22taxonomies.seller_type%22%2C%22taxonomies.taxonomies_hierarchical.product_cat.lvl0%22%2C%22taxonomies.taxonomies_hierarchical.product_cat.lvl1%22%5D&tagFilters=&facetFilters=%5B%5B%22taxonomies.taxonomies_hierarchical.product_cat.lvl0%3A{}%22%5D%5D"},{"indexName":"products_index","params":"query=&hitsPerPage=1&maxValuesPerFacet=20&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&getRankingInfo=1&filters=post_status%3Apublish%20AND%20price%3E0%20AND%20archive%3A0%20AND%20in_stock%3A1%20%20AND%20taxonomies.erp_ver%3A2&clickAnalytics=true&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&facets=%5B%22taxonomies.taxonomies_hierarchical.product_cat.lvl0%22%5D"}]}

    

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    page = 0
    count = 0
    item_reviews = []
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
    
    categories = {
        'Mobiles': 'Mobiles%20%26%20Tablets',
        'Health Fitness Beauty': 'Health%2C%20Fitness%20%26%20Beauty',
        'Computing': 'Computing',
        'Television and Audio': 'TV%2C%20Video%20%26%20Audio',
        'Wearables and Smartwatches': 'Wearables%20%26%20Smartwatches',
        'Home': 'Home%20Appliances',
        'Gaming': 'Gaming',
        'Cameras Camcorders': 'Cameras%20%26%20Camcorders'
            }
    
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
            catalogue_code = self.get_catalogue_code(category)
            if catalogue_code:
                modified_body = copy.deepcopy(self.body)      
                formatted_body = modified_body["requests"][0]["params"].format(self.page, formatted_category)
                modified_body["requests"][0]["params"] = formatted_body
                body = json.dumps(modified_body)
                yield scrapy.Request(url=self.products_api, headers=self.headers, method='POST', body=body, callback=self.parse, meta={'category': category, 'formatted_category': formatted_category, 'page': self.page, 'catalogue_code': catalogue_code})

    def parse(self, response):
        category = response.meta['category']
        formatted_category = response.meta['formatted_category']
        page = response.meta['page']
        data = json.loads(response.text)
        results = data.get('results', [])[0]
        hits = results.get('hits')
        if hits:
            for hit in hits:
                
                title = hit.get('post_title', '')
                sku = hit.get('main_sku', '')
                img = hit.get('images', '')
                url = hit.get('permalink', '')
                price_in_aed = hit.get('regular_price', 0)
                price_in_aed = round(float(price_in_aed), 2)
                sale_price_in_aed = hit.get('sale_price', 0)
                sale_price_in_aed = round(float(sale_price_in_aed), 2)
                if not sale_price_in_aed:
                    sale_price_in_aed = 0
                brand = hit.get('taxonomies', {}).get('product_brand', [])[0]
                sub_categories_dict = hit.get('taxonomies', {}).get('taxonomies_hierarchical', {}).get('product_cat', {})
                if sub_categories_dict:
                    last_lvl_key = sorted(sub_categories_dict.keys())[-1]  # Get the last key in the hierarchy
                    sub_categories = sub_categories_dict[last_lvl_key] 
                else:
                    sub_categories = ''

                in_stock = hit.get('in_stock', 1)
                discount_percentage = hit.get('discount', '')
                if not discount_percentage:
                    discount_percentage = ''
                 
                discount_value = hit.get('discount_val', 0)
                if not discount_value:
                    discount_value = 0
                rating = hit.get('rating_reviews', {})

                if rating:
                    rating = rating.get('rating', 0)
                    rating = round(float(rating), 2)
                else:
                    rating = 0
                
                review_count = hit.get('rating_reviews', {})
                if review_count:
                    ReviewCount = review_count.get('reviews', 0)
                else:
                    ReviewCount = 0

                catalogue_code = response.meta['catalogue_code']
                category_code = self.get_category_code(sub_categories, catalogue_code)
                vendor_code = self.vendor_code
                

                yield scrapy.Request(url=self.review_api_1.format(sku), callback=self.parse_pid, 
                    meta={
                    'title': title, 
                    'sku': sku,
                    'img': img,
                    'url': url,
                    'price_in_aed': price_in_aed,
                    'sale_price_in_aed': sale_price_in_aed,
                    'brand': brand,
                    'sub_categories': sub_categories,
                    'in_stock': in_stock,
                    'discount_percentage': discount_percentage,
                    'discount_value': discount_value,
                    'rating': rating,
                    'category': category,
                    'page': page,
                    'ReviewCount': ReviewCount,
                    'CatalogueCode': catalogue_code,
                    'CategoryCode': category_code,
                    'VendorCode': vendor_code,
                    })
          
            #Next Page
            page = page + 1
            modified_body = copy.deepcopy(self.body)      
            formatted_body = modified_body["requests"][0]["params"].format(page, formatted_category)
            modified_body["requests"][0]["params"] = formatted_body
            body = json.dumps(modified_body)
            yield scrapy.Request(url=self.products_api, headers=self.headers, method='POST', body=body,  meta={'category': category, 'formatted_category': formatted_category, 'page': page, 'catalogue_code': catalogue_code})


    def parse_pid(self, response):
        item = ProductItemSharafDG()
        item['ProductName'] = response.meta['title']
        item['SKU'] = response.meta['sku']
        item['MainImage'] = response.meta['img']
        item['URL'] = response.meta['url']
        item['RegularPrice'] = response.meta['price_in_aed']
        item['Offer'] = response.meta['sale_price_in_aed']
        item['BrandName'] = response.meta['brand']
        item['CategoryName'] = response.meta['sub_categories']
        item['StockAvailability'] = response.meta['in_stock']
        item['RatingValue'] = response.meta['rating']
        item['CatalogueName'] = response.meta['category']
        #item['ReviewCount'] = response.meta['ReviewCount']
        item['CatalogueCode'] = response.meta['CatalogueCode']
        item['CategoryCode'] = response.meta['CategoryCode']
        item['VendorCode'] = response.meta['VendorCode']

        #item['ModelName'] = ''
        item['ModelNumber'] = ''
        #item['ProductDesc'] = ''
        #item['SubBrandName'] = ''
        item['BrandCode'] = ''
        #item['BestRating'] = 0

        data = json.loads(response.text)
        pid_url = data.get('user_review_url')
        if pid_url:
            pid_match_re = re.search(r'pid=(\d+)', pid_url)
            if pid_match_re:
                pid = pid_match_re.group(1)
                yield scrapy.Request(url=self.review_api_2.format(pid), callback=self.parse_review, 
                                                         meta={
                                                            'ProductName': item['ProductName'], 
                                                            'SKU': item['SKU'],
                                                            'MainImage': item['MainImage'],
                                                            'URL': item['URL'],
                                                            'RegularPrice': item['RegularPrice'],
                                                            'Offer': item['Offer'],
                                                            'BrandName': item['BrandName'],
                                                            'CategoryName': item['CategoryName'],
                                                            'StockAvailability': item['StockAvailability'],
                                                            'RatingValue': item['RatingValue'],
                                                            'CatalogueName': item['CatalogueName'],
                                                            #'ReviewCount': item['ReviewCount'],
                                                            'CatalogueCode': item['CatalogueCode'],
                                                            'CategoryCode': item['CategoryCode'],
                                                            'VendorCode': item['VendorCode']
                                                            
                                                            })
            else:
                print("PID not found in user_review_url: %s", pid_url)
        else:
            #print('user_review_url not found in response data.')
            yield item


    def parse_review(self, response):
        item = ProductItemSharafDG()
        item_reviews = []

        item['ProductName'] = response.meta['ProductName']
        item['SKU'] = response.meta['SKU']
        item['MainImage'] = response.meta['MainImage']
        item['URL'] = response.meta['URL']
        item['RegularPrice'] = response.meta['RegularPrice']
        item['Offer'] = response.meta['Offer']
        item['BrandName'] = response.meta['BrandName']
        item['CategoryName'] = response.meta['CategoryName']
        item['StockAvailability'] = response.meta['StockAvailability']
        item['RatingValue'] = response.meta['RatingValue']
        item['CatalogueName'] = response.meta['CatalogueName']
        #item['ReviewCount'] = response.meta['ReviewCount']
        item['CatalogueCode'] = response.meta['CatalogueCode']
        item['CategoryCode'] = response.meta['CategoryCode']
        item['VendorCode'] = response.meta['VendorCode']
        #item['ModelNumber'] = response.xpath('//ul[@class="specifications-list"]/li[@class="row list-li"][1]//div[@class="pdp-specifications-block"][4]/div[@class="flex"]/div[@class="w-60"]/text()').get()
        #item['ModelName'] = ''
        item['ModelNumber'] = ''
        #item['ProductDesc'] = ''
        #item['SubBrandName'] = ''
        item['BrandCode'] = ''
        
        # item['BestRating'] = response.xpath('//li[@class="rating-progress"][1]/div[@class="star-count"]/h6/text()').get()
        # item['Rating5'] = response.xpath('//li[@class="rating-progress"][1]/div[@class="star-count-total"]/h6/text()').get()
        # item['Rating4'] = response.xpath('//li[@class="rating-progress"][2]/div[@class="star-count-total"]/h6/text()').get()
        # item['Rating3'] = response.xpath('//li[@class="rating-progress"][3]/div[@class="star-count-total"]/h6/text()').get()
        # item['Rating2'] = response.xpath('//li[@class="rating-progress"][4]/div[@class="star-count-total"]/h6/text()').get()
        # item['Rating1'] = response.xpath('//li[@class="rating-progress"][5]/div[@class="star-count-total"]/h6/text()').get()
        data = json.loads(response.text)
        # comment = ''
        # source = ''
        # comment_date = ''
        
        reviews = data.get('reviews', [])
        

        if reviews:
            for review in reviews:
                comment = review.get('extract', '')
                source = review.get('source', '')
                comment_date = review.get('date', '')
                rating = round(float(review.get('score')) / 2, 2)
                max_rating = round(float(review.get('score_max')) / 2, 2)

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
            #item['BestRating'] = max_rating
            
        else:
            pass
            # If no reviews are found, set default values for review fields
            # item['reviews'] = [{
            #     'Comment': '',
            #     'Source': '',
            #     'CommentDate': '',
            #     'rating': 0,
            #     'max_rating': 0,
            #     'average_rating': item['RatingValue']
            # }]

            #item['BestRating'] = 0


        
        yield item
        #else:
            # item['Comment'] = ''
            # item['Source'] = ''
            # item['CommentDate'] = ''



        # review_list = response.css(".review-list")
        # if review_list:
        #     for review in review_list:
        #         item['Comment'] = review.css("#userReview p::text").get()
        # else:
        #     item['Comment'] = ''

        #yield item



        #NEXT PAGE



        
        




