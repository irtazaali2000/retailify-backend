# -*- coding: utf-8 -*-
import json
import re
import django
import requests
from scrapy import Spider, Request
from scrapy import Selector
from datetime import datetime
from ..settings import HOST, CATALOGUE_URL_T
from urllib.parse import unquote
from ecom_crawlers.utils import *


class NoonOldSpider(Spider):
    name = 'noon_old'
    handle_httpstatus_list = [404]

    product_url_t = 'https://www.noon.com/uae-en/{}/{}/p'
    # search_url = 'https://www.noon.com/_svc/catalog/api/search'
    #search_url = 'https://www.noon.com/_svc/catalog/api/v3/u/'
    search_url = 'https://www.noon.com/_svc/catalog/api/v3/u/all-p-fbn-ae/'


    search_body_t = '{{"brand":[],"category":["{}"],"filterKey":[],"f":{},"sort":{{"by":"popularity","dir":"desc"}},"limit":100,"page":{}}}'

    headers = {
        'content-type': 'application/json',
        #'User-Agent': USER_AGENT
    }

    # print("############################################")
    # #print(headers['User-Agent'])
    depart_regex = "\[(.*)\]=(.*)"

    image_url_t = 'https://k.nooncdn.com/t_desktop-pdp-v1/{}.jpg'
    category_url_t = 'https://www.noon.com/uae-en/{}'

    rating_url_t = 'https://www.noon.com/_svc/mp-trust-api/product-reviews/sku/list/'
    
    test_shelve_only = False
    test_urls = [
        "https://www.noon.com/uae-en/13s-iwl-laptop-with-13-3-inch-display-core-i5-processer-16gb-ram-256gb-ssd-intel-uhd-graphics-mineral-grey/N41420338A/p",
        # 'https://www.noon.com/uae-en/low-ph-good-morning-gel-cleanser-150ml/N14352576A/p',
        # 'https://www.noon.com/uae-en/search?q=Washing%20machine'
    ]

    custom_settings = {
        # "CONCURRENT_REQUESTS": 250,
        #'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
        'DOWNLOAD_DELAY': 0.75,
        'DOWNLOAD_TIMEOUT': 600,  # Increase to 600 seconds or as needed
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408],
        # 'LOG_STDOUT': True,
        # 'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
    }


    def __init__(self, reviews='False', short_scraper="False", *args, **kwargs):
        self.reviews = reviews.lower() == 'true'
        self.short_scraper = short_scraper.lower() == 'true'
        catalogue_url = CATALOGUE_URL_T.format(self.name, self.short_scraper)
        categories_url = "{}{}".format(HOST, catalogue_url)

        #print(f"Fetching categories from: {categories_url}")

        raw_res = requests.get(categories_url)
        #print(f"Response status code: {raw_res.status_code}")
        
        if raw_res.status_code == 200:
            try:
                raw_data = raw_res.json()
                self.categories = raw_data.get('data', [])
                self.vendor_code = raw_data.get('VendorCode')
                #print("#################################")
                #print(self.categories)
                #print(self.vendor_code)
                #print("#################################")
            except json.decoder.JSONDecodeError:
                print(f"Failed to parse JSON from response: {raw_res.text}")
        else:
            print(f"Failed to get data from {categories_url}. Status code: {raw_res.status_code}")

        
        

    def parse_error(self, failure):
        if failure.value.response.status == 404:
            print("a")

    def prepare_body(self, cat):
        #print(f"Preparing body for category: {cat}")

        search_body_temp = {
            "brand": [],
            "category": [],
            "filterKey": [],
            "f": {},
            "sort": {
                "by": "popularity",
                "dir": "desc"
            },
            "limit": 100,
            "page": 1
        }

        departments = None
        department_filter = dict()
        cat = '/'.join(cat.split('/')[4:])
   
        if '?' in cat:
            cat, departments = cat.split('?')

            department_filter = dict()
            if departments:
                for department in departments.split('&'):
                    if 'q' in department:
                        searchkey, searchvalue = department.split('=')
                        search_body_temp[f'{searchkey}'] = unquote(searchvalue)
                        search_body_temp[f'original_{searchkey}'] = unquote(searchvalue)

                    if 'f[' in department:
                        depart, val = re.findall(r'{}'.format(self.depart_regex), department)[0]
                        if not department_filter.get(depart):
                            department_filter[depart] = list()

                        department_filter[depart].append(val)
                        search_body_temp['f'] = json.dumps(department_filter)

        search_body_temp['category'] = [cat]
        return search_body_temp, department_filter



    def start_requests(self):
        #print("Start Requests called!")

        if self.test_shelve_only:
            for url in self.test_urls:
                yield Request(url,
                              callback=self.parse,
                              # errback=self.parse_error
                              )
            return

        for category in self.categories:
            for multi_cat in category['CategoryName'].split(','):
                #print(f"Processing category: {multi_cat}")
                # if multi_cat == "https://www.noon.com/uae-en/search?q=Washing%20machine":
                if True:
                    body, department_filter = self.prepare_body(multi_cat)
                    #print(f"Body for category: {body}")
                    #print(f"Request to search API: {self.search_url}")
                    #print(f"Request headers: {self.headers}")
                    #print(f"Request body: {json.dumps(body)}")

                    meta = {
                        'category': category,
                        'department': department_filter,
                        'link': multi_cat,
                        'page': 1
                    }

                    #print(f"Requesting search API for category: {multi_cat}")
                    print("Category: ", category)
                    print("Link: ", multi_cat)
                    yield Request(
                        url=self.search_url,
                        callback=self.parse_product_links,
                        #dont_filter=True,
                        #body=json.dumps(body),
                        #headers=self.headers,
                        method='GET', #Ye pehle POST tha
                        meta=meta.copy()
                    )

    def parse_product_links(self, response):
        meta = response.meta.copy()
        raw_products = json.loads(response.text)
        
        total_pages = raw_products.get('nbPages', 1)
        current_page = meta['page']
        
        print(f"Category: {meta['link']}, Page: {current_page}, Total Pages: {total_pages}")


        for product in raw_products.get('hits', []):
            new_meta = meta.copy()
            new_meta['product'] = product  # Add the product information to the new meta

            yield Request(
                self.product_url_t.format(
                    product['url'], product['sku'],
                ),
                callback=self.parse_product,
                meta=new_meta
            )


        if current_page < total_pages:
            print("Gone to next page")
            page = current_page + 1
            new_meta = meta.copy()
            new_meta['page'] = page
            body, department_filter = self.prepare_body(new_meta['link'])
            body['page'] = page

            print(f"Requesting search API for category (next page): {new_meta['link']}, Page: {new_meta['page']}")

            yield Request(
                url=self.search_url,
                callback=self.parse_product_links,
                body=json.dumps(body),
                headers=self.headers,
                method='GET',
                meta=new_meta
            )
        else:
            print("No more pages to request.")

    # def parse_product_links(self, response):
    #     meta = response.meta.copy()
    #     raw_products = json.loads(response.text)
        
    #     total_pages = raw_products.get('nbPages', 1)
    #     current_page = meta['page']
        
    #     print(f"Category: {meta['link']}, Page: {current_page}, Total Pages: {total_pages}")

    #     products = raw_products.get('hits', [])
    #     if products:
    #         for product in products:
    #             new_meta = meta.copy()
    #             new_meta['product'] = product  # Add the product information to the new meta

    #             yield Request(
    #                 self.product_url_t.format(
    #                     product['url'], product['sku'],
    #                 ),
    #                 callback=self.parse_product,
    #                 meta=new_meta
    #             )
    #     else:
    #         print("No products found on this page.")

    #     if current_page < total_pages:
    #         print("Gone to next page")
    #         page = current_page + 1
    #         new_meta = meta.copy()
    #         new_meta['page'] = page
    #         body, department_filter = self.prepare_body(new_meta['link'])
    #         body['page'] = page

    #         print(f"Requesting search API for category (next page): {new_meta['link']}, Page: {new_meta['page']}")

    #         yield Request(
    #             url=self.search_url,
    #             callback=self.parse_product_links,
    #             body=json.dumps(body),
    #             headers=self.headers,
    #             method='GET',
    #             meta=new_meta
    #         )
    #     else:
    #         print("No more pages to request.")

    def parse_product(self, response):
        #("Parsing product details!")
        print('ALOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
        raw_data = json.loads(response.xpath('//*[@id="__NEXT_DATA__"]/text()').get({}))
        if not raw_data:
            return

        currency_code = raw_data.get('props', {}).get('locale', {}).get('currencyCode')
        product = response.meta.get('product')  
        raw_product = raw_data.get(
            'props', {}
        ).get(
            'pageProps', {}
        ).get(
            'catalog', {}
        ).get(
            'product', {}
        )
        item = dict()
        category = response.meta.get('category')

        #print(f"Crawling product details for URL: {response.url}")

        if not(self.test_shelve_only):
            item['VendorCode'] = self.vendor_code
            item['CatalogueCode'] = category['CatalogueCode']
            item['CategoryCode'] = category['CategoryCode']

        breadcrumbs = raw_product.get('breadcrumbs', {})
        if breadcrumbs:
            item['CatalogueName'] = breadcrumbs[0].get('name', 'N/A')
            item['CategoryName'] = breadcrumbs[-1].get('name', 'N/A')
        else:
            item['CatalogueName'] = 'N/A'
            item['CategoryName'] = 'N/A'
        item['ProductName'] = raw_product.get('product_title')
        highlights = [" | ".join(raw_product.get('feature_bullets', []))]
        raw_desc = raw_product.get('long_description')
        if raw_desc is not None:
            raw_desc = raw_desc.replace('\n', '')
        else:
            raw_desc = ''

        highlights.extend('\n\n')
        highlights.extend(raw_desc)
        item['ProductDesc'] = "".join(highlights)

        highlights.extend('\n\n')
        highlights.extend(raw_desc)
        item['ProductDesc'] = "".join(highlights)
        images = raw_product.get("image_keys")
        item['MainImage'] = self.image_url_t.format(images[0])
        item['images'] =[self.image_url_t.format(image) for image in images]
        item.get('images').remove(item['MainImage'])
        item['URL'] = response.url
        item['SKU'] = raw_product.get('sku')
        item['BrandName'] = raw_product.get('brand') or 'N/A'
        if not item['BrandName']:
            pass

        item['AdditionalProperty'] = [
            {
                'name': spec.get('name'),
                'value': spec.get('value')
            }
            for spec in raw_product.get('specifications', [])
        ]

        model_name = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model name']
        model_name = model_name[0] if model_name else None
        item['ModelName'] = model_name

        model_number = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model number']
        model_number = model_number[0] if model_number else None
        item['ModelNumber'] = model_number

        item['StockAvailability'] = self.get_stock_availability(raw_product.get('variants', []), response)
        item['RegularPrice'] = clean_money_str("".join(response.css('div .priceNow::text').extract()))
        item['Offer'] = clean_money_str('')

        if response.css('div .priceWas::text').extract():
            item['Offer'] = item['RegularPrice']
            item['RegularPrice'] = clean_money_str("".join(response.css('div .priceWas::text').extract()))

        return Request(
            self.rating_url_t.format(product['url'], product['sku'], item['SKU']),
            self.parse_rating,
            method = 'POST',
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
            },
            body=json.dumps({
                "sku": item['SKU'],
                "lang": "en",
                "ratings": [1, 2, 3, 4, 5],
                "provideBreakdown": True,
                "page": 1,
                "perPage": 15,
                "sortFilter": "helpful"
            }),
            meta={'item': item.copy()}
        )


    def filter_list(self, descriptions):
        raw_description = [clean_val(description) for description in descriptions]
        return list(filter(None, raw_description))

    def parse_rating(self, response):
        #print("Parsing product ratings!")

        item = response.meta.get('item')
        item['reviews'] = list()
        item['Rating'] = dict()

        try:
            data = json.loads(response.text)
        except json.decoder.JSONDecodeError as e:
            print(f"Failed to decode JSON from response!") #{response.text}
            print(f"Error details: {e}")
            return item

        rating = data.get('summary')
        if not rating:
            item['RatingValue'] = 0
            item['BestRating'] = 0
            item['ReviewCount'] = 0
            return item

        # For inserting the data in product_product table
        summary = data.get('summary', {})
        item['RatingValue'] = summary.get('rating', 0)
        item['BestRating'] = summary.get('count', 0)
        item['ReviewCount'] = summary.get('commentCount', 0)

        # For inserting the data in product_review table
        for review_data in data.get('list', []):
            review_item = {
                'Comment': review_data.get('comment', ''),
                'CommentDate': review_data.get('updatedAt', None),
                'Source': 'noon'  # Assuming a source identifier
            }
            item['reviews'].append(review_item)


        # For inserting the data in product_rating table
        for rating_data in data.get('list', []):
            rating_item = {
                'Rating1': '1' if rating_data.get('rating', 0) == 1 else '0',
                'Rating2': '1' if rating_data.get('rating', 0) == 2 else '0',
                'Rating3': '1' if rating_data.get('rating', 0) == 3 else '0',
                'Rating4': '1' if rating_data.get('rating', 0) == 4 else '0',
                'Rating5': '1' if rating_data.get('rating', 0) == 5 else '0',
            }
            item['Rating']= rating_item


        # conn = pymysql.connect(
        #     host='localhost',
        #     user='root',
        #     password='admin',
        #     database='gbscrapper',
        #     charset='utf8mb4',
        #     cursorclass=pymysql.cursors.DictCursor
        # )

        # try:
        #     with conn.cursor() as cursor:
        #         for review_data in raw_reviews.get('list', []):
        #             cursor.execute("SELECT ProductCode FROM product_product Where SKU = %s", (item['SKU'],))
        #             result = cursor.fetchone()
        #             if result:
        #                 productcode_id = result['ProductCode']
        #             sql = "INSERT INTO product_review (Comment, SKU, CommentDate, DateInserted, DateUpdated, is_active, Source, ProductCode_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        #             cursor.execute(sql, (review_data.get('comment', ''), item['SKU'], review_data.get('updatedAt', None), datetime.now(), datetime.now(), True, "", productcode_id))
        #         conn.commit()
        # finally:
        #     conn.close()
  
    
        return item



    def get_stock_availability(self, variants, response):
        raw_stocks = response.css('div.first-subtitle1 ::text').extract()
        availability = [item.lower() for item in raw_stocks]
        available = 'add to cart' in availability
        if available:
            return available
        else:
            return available

        # for variant in variants:
        #     if variant.get('offers'):
        #         return True
        #     else:
        #         pass
        #
        # return False
