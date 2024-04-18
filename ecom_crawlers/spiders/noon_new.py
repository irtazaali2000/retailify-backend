import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemNoon
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import mysql.connector



class NoonSpider(Spider):
    name = 'noon'
    allowed_domains = ['noon.com']
    main_url = 'https://www.noon.com'
    url_product_template = 'https://www.noon.com/uae-en/{}/{}/p/'
    img_product_template = 'https://f.nooncdn.com/p/{}.jpg'
    review_url = 'https://www.noon.com/_svc/mp-trust-api/product-reviews/sku/list/'
    body = {
        "sku": "{}",
        "lang": "xx",
        "ratings": [1, 2, 3, 4, 5],
        "provideBreakdown": True,
        "page": 1,
        "perPage": 15,
        "sortFilter": "helpful",
        "imagesFilter": False
    }


    headers = {
        'authority': 'www.noon.com',
        'method': 'GET',
        'path': '/_svc/catalog/api/v3/u/electronics-and-mobiles/all-p-fbn-ae/?limit=50&page=0&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'scheme': 'https',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://www.noon.com/uae-en/electronics-and-mobiles/all-p-fbn-ae/?limit=50&page=3&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'X-Aby': '{"ipl_entrypoint_v2.enabled":1,"ipl_v2.enabled":1,"noon_pass.enabled":1,"otp_login.enabled":1,"pdp_bos.enabled":1,"pdp_flyout.flyout_value":0,"pp_entrypoint.enabled":1,"second_tab_screen.name":"dynamicTab"}',
        'X-Cms': 'v3',
        'X-Content': 'desktop',
        'X-Lat': '25.1998495',
        'X-Lng': '55.2715985',
        'X-Locale': 'en-ae',
        'X-Mp': 'noon',
        'X-Platform': 'web',
        'X-Visitor-Id': '3c2883ca-1b7f-454b-96f4-cbe9b90bc0db'
    }

    review_headers = {
    'authority': 'www.noon.com',
    'method': 'POST',
    'path': '/_svc/catalog/api/v3/u/electronics-and-mobiles/all-p-fbn-ae/?limit=50&page=0&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    'scheme': 'https',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/json',
    'Cookie': 'nloc=en-ae; visitor_id=3c2883ca-1b7f-454b-96f4-cbe9b90bc0db; _gcl_au=1.1.1385826969.1708068654; _ga=GA1.2.1968629218.1708068654; _fbp=fb.1.1708068654293.1845911762; _scid=066f7c4a-e8e7-464b-9391-07d9cf77d3ba; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22AHmwZChPEsw40oHXrnfv%22%7D; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3Anull%7D; _ym_uid=1708068656794109551; _ym_d=1708068656; _tt_enable_cookie=1; _ttp=dk024lX8-6qZxhog6-umXZWkwB2; __zlcmid=1KLmV9L8yUZ5bji; _gid=GA1.2.2093820198.1712149497; _sctr=1%7C1712098800000; review_lang=xx; x-available-ae=ecom; _clck=18plloi%7C2%7Cfkn%7C0%7C1507; bm_mi=1BD0DA255C892C7E4CEFC27DD1FCC9DC~YAAQHtYsF1IiLYqOAQAA4UTJpxdeooJorwOcZPwHNOCx8YOLVokWx2PGDb9RfAdlTThddtt0HU29exeUeVwGJTaHTiCP35/N1DrVhdJPSehtHRD9OP5NJtmSyATOA95Z5EvOe+FFLZUKFdkKOtuaqQMELRDxEY8RgSTXUkjqEi2NamzjTsyeHRNYdGFsxuI/mDiQYZfz4PredUb6SXX9OtyfVU+qXHLmb+WIiz5mAj5TcnN2fzvaym6wpksFM/YaVCw+B2B3REbrvYviPTUePemnRFCUAV/Gts9LEi0MvTyRT2CuF/oDwWmX0Hd1S4VG+zH2Yyj4JCatOJtKuxv7NxfnczgrLGSwLp5J0ljGclNGkja8ah1YJQ2o~1; ak_bmsc=7692BC37019E2CC063A252F821ED2797~000000000000000000000000000000~YAAQHtYsFwkkLYqOAQAAl1vJpxcNvXXcTGfAzS5ZASWYekmIoZ2/gbqGctTGE+TIWXKi1mV1CSfJDHOxUc0/GTtvA8oK2E0EaUCLw7IRGzdoGGYIMOQhvFRgcB572CW6Y3fB93L7BdFESr8IrzUQjbZwXsELZObCpD6Hlq87+P0DwtA0ryiZXOUs5uibe5ClphtSD4HAWJEWbHrWar6rNsq1PWle2z4H4P9QX4cuZX6+Y3yE8a4K1YAxiyeXcUQAUWFoZ1Wwewp4b/4iJCU9XyGIl4oMRKGie5y911wP2wgTTR3LvKjKzsjQmv6ysA4RqHbzCPt5DQDCffgHtix9bw0IPi1r/oG/HEYX1PRfFp4wnDBgtTE8ssxEUI169bKtg5G++r1lZ8EVXF3SJg8n0fyoCb2YcqGfFGj42YdC1Bj1V7LanMARxnmY7rXS1nYGsl6e7Xe5IOU99VWqNUgybYk3o0ddLGNSfdoxCAzZllYt1G0U8uz4JpBJlOiDjxDgZCMlboR0+Vsvh26bywCgvUSrhcgInM357Zs=; nguestv2=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJraWQiOiIzNDgyM2Q4YjIwZTY0NmFkYjI3MDJhYTYxZGZmZmU3NyIsImlhdCI6MTcxMjIxNTU1MCwiZXhwIjoxNzEyMjE1ODUwfQ.eHJWz_krMAHLvjjc2K4HPicn6AnVA0915XCUugIKDJc; nguestv2=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJraWQiOiI5YzJhMWZhMGRjNzU0YzdhODZjMjc2Zjg3ZDZmMmE1YyIsImlhdCI6MTcxMjIxNTU1MCwiZXhwIjoxNzEyMjE1ODUwfQ.YhBiuifJO-_hre9nPy8fm5SMV5kNvsmoFZ35DXgpKI8; __gads=ID=cf09f66d54094f68:T=1708083477:RT=1712215556:S=ALNI_MbhO83HKhGOCQQXQfdmmgjzm3Bogw; __gpi=UID=00000d23c624ba7a:T=1708083477:RT=1712215556:S=ALNI_MZAib_JwuvOsSphAgVFFx2j90A6TA; __eoi=ID=be755f0761063099:T=1708083477:RT=1712215556:S=AA-AfjbM-lVVgN8Os2C26-PAXtdi; _gat_UA-84507530-14=1; AKA_A2=A; _scid_r=066f7c4a-e8e7-464b-9391-07d9cf77d3ba; _uetsid=c57de2c0f1ba11ee8599cbb1529eb0d7; _uetvid=51c70f60cc9d11ee865e110d922a87f2; _clsk=xi50s1%7C1712215602267%7C22%7C0%7Ci.clarity.ms%2Fcollect; RT="z=1&dm=noon.com&si=cd4a450b-2adf-4ab3-9dd9-d834c2870f02&ss=lukuqliy&sl=g&tt=1hv6&obo=e&rl=1"; _etc=txe834bT7NewcK0A; bm_sv=4DEC2F57465F52E51024C8EEB5EA6DB7~YAAQHtYsF9xTMYqOAQAAQs0AqBfCgODjz+zWs7Cu37YMNHWzkZZfUjH14QGHe8n9URraxTg3cmzCE4sdllKH8AFhrROl/MCBJHtN+Mp5hW5lDhWqcWLzzQ9l6/shduYiLdv1Hc4OEnWGMcTGhRWpRdFovUmWZEF85V6yfGEhy3yaZWhgKiYYE0xuTzS22pq/bUU+v/k56L7dNe+cQOYAcQ+KH0ZxsIzAeVVnNLDSJt9IkeohHGPnwo5p/UMCR0p/~1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408],
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    categories = {
        'Electronics and Mobiles': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/all-p-fbn-ae/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Fashion': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Electronics': 'https://www.noon.com/_next/data/820f335dc16eebbfe1bb2be8abbf8837ce821a6d/uae-en/electronics-and-mobiles/all-p-fbn-ae.json?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc&catalog=electronics-and-mobiles&catalog=all-p-fbn-ae',
        'Home and Kitchen': 'https://www.noon.com/_svc/catalog/api/v3/u/home-and-kitchen/all-p-fbn-ae/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Beauty and Fragrance': 'https://www.noon.com/_svc/catalog/api/v3/u/beauty/all-p-fbn-ae/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Books': 'https://www.noon.com/_svc/catalog/api/v3/u/books/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Toys and Games': 'https://www.noon.com/_svc/catalog/api/v3/u/toys-and-games/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Tools and Home Improvement': 'https://www.noon.com/_svc/catalog/api/v3/u/tools-and-home-improvement/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Baby Products': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Sports, Fitness and Outdoors': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Office Supplies': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Health and Nutrition': 'https://www.noon.com/_svc/catalog/api/v3/u/health/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Automotive': 'https://www.noon.com/_svc/catalog/api/v3/u/automotive/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Pet Supplies': 'https://www.noon.com/_svc/catalog/api/v3/u/pet-supplies/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Music, Movies and TV Shows': 'https://www.noon.com/_svc/catalog/api/v3/u/music-movies-and-tv-shows/all-p-fbn-ae/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Gift Card and Subscription Vouchers': 'https://www.noon.com/_svc/catalog/api/v3/u/gift-card-subscription-vouchers/all-p-fbn-ae/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc'
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
        for category, cat_url in self.categories.items():
            catalogue_code = self.get_catalogue_code(category)
            if catalogue_code:
                yield scrapy.Request(url=cat_url.format(self.page), headers=self.headers, meta={'category': category, 'cat_url': cat_url, 'page': self.page, 'catalogue_code': catalogue_code})



    def parse(self, response):
        item = ProductItemNoon()
        data = json.loads(response.text)
        page = response.meta['page']
        cat_url = response.meta['cat_url']
        vendor_code = self.vendor_code
        item['CatalogueName'] = response.meta['category']
        sub_category = data.get('analytics',{}).get('ed', {}).get('pcat', [])
        if sub_category:
            item['CategoryName'] = sub_category[0]
        hits = data.get("hits", [])
        if hits:
            for hit in hits:
                item['SKU'] = hit.get('sku')
                item['BrandName'] = hit.get('brand')
                item['ProductName'] = hit.get('name')
                item['ProductName'] = item['ProductName'].strip()
                item['RegularPrice'] = hit.get('price')
                item['RegularPrice'] = round(float(item['RegularPrice']), 2)
                item['Offer'] = hit.get('sale_price')
                item['Offer'] = round(float(item['Offer']), 2)
                item['StockAvailability'] = hit.get('is_buyable')
                item['RatingValue'] = hit.get('product_rating', {}).get('value', 0)
                item['RatingValue'] = round(float(item['RatingValue']), 2)
                url = hit.get('url')
                item['URL'] = self.url_product_template.format(url, item['SKU'])
                img = hit.get('image_key')
                item['MainImage'] = self.img_product_template.format(img)
                item['ModelNumber'] = hit.get('plp_specifications', {}).get('Model Number')
                if not item['ModelNumber']:
                    item['ModelNumber'] = ''

                item['VendorCode'] = vendor_code
                item['BrandCode'] = ''
                catalogue_code = response.meta['catalogue_code']
                category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                item['CatalogueCode'] = catalogue_code
                item['CategoryCode'] = category_code

                
                updated_body = {k: v.format(item['SKU']) if isinstance(v, str) else v for k, v in self.body.items()}
                yield scrapy.Request(url=self.review_url, headers=self.review_headers, method='POST', body=json.dumps(updated_body), callback=self.parse_review, meta={'item': item})
            
            #NEXT PAGE
            page = page + 1
            yield scrapy.Request(url=cat_url.format(page), headers=self.headers, meta={'category': item['CatalogueName'], 'cat_url': cat_url, 'page': page, 'catalogue_code': catalogue_code})


    def parse_review(self, response):
        item = response.meta['item']
        data = json.loads(response.text)
        item_reviews = []
        list = data.get('list', [])
        if list:
            for review in list:
                comment = review.get('comment', '')
                source = ''
                comment_date = review.get('updatedAt', '')
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
     





