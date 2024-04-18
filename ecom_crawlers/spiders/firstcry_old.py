import csv
import math
import json
import logging

import requests
import w3lib.url
import urllib.parse as urlparse
from urllib.parse import parse_qs
from datetime import datetime

from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Spider

from ..settings import HOST, CATALOGUE_URL_T
from ecom_crawlers.utils import *

LOGGER = logging.getLogger(__name__)


class FirstCryProduct(Spider):
    name = "firstcry-parse"
    image_url_t = 'https://cdn.ae1stcry.com/brainbees/images/products/438x531/{}'
    test_shelve_only = False

    def parse_item(self, response):
        product_price = response.css('#prod_price::text').extract()

        product_details = response.meta['product_details']
        category = response.meta.get('category')
        vendor_code = response.meta.get('vendor_code')
        product = {}

        if not (self.test_shelve_only):
            product['VendorCode'] = vendor_code
            product['CatalogueCode'] = category['CatalogueCode']
            product['CategoryCode'] = category['CategoryCode']

        product['URL'] = response.url

        product['CatalogueName'] = product_details['CNm']
        product['CategoryName'] = product_details['SCNm']
        product['ProductName'] = product_details['PNm']
        product['ProductDesc'] = product_details['PDsc']
        product['MainImage'] = response.css('.prod-img .big-img::attr(src)').extract_first()
        product['images'] = [self.image_url_t.format(p) for p in product_details['Images'].split(';')]

        product['SKU'] = product_details['PId']
        product['BrandName'] = product_details['BNm']

        raw_rating = response.css('#star_value::text').extract_first()
        product['RatingValue'] = float(raw_rating if raw_rating else 0.0)
        product['BestRating'] = self.best_rating(response)
        product['Rating'] = self.rating(response, product)

        product['ReviewCount'] = self.review_count(response)

        product['AdditionalProperty'] = self.additional_property(product_details)

        product['StockAvailability'] = True if product_price else False
        disc_price = clean_money_str(product_details['discprice'])
        price = clean_money_str(product_details['MRP'])
        product['Offer'] = clean_money_str('')
        if disc_price != price:
            product['RegularPrice'] = price
            product['Offer'] = disc_price
        else:
            product['RegularPrice'] = price

        return product

    def additional_property(self, product_details):
        additional_properties = []
        if product_details.get('shippingdate'):
            additional_properties.append({
                'name': 'ShippingDate',
                'value': product_details['shippingdate']
            })

        if product_details.get('shippinghours'):
            additional_properties.append({
                'name': 'ShippingHours',
                'value': product_details['shippinghours']
            })

        if product_details.get('size'):
            additional_properties.append({
                'name': 'Size',
                'value': product_details['size']
            })

        if product_details.get('color'):
            additional_properties.append({
                'name': 'Color',
                'value': product_details['color']
            })

        if product_details.get('CrntStock'):
            additional_properties.append({
                'name': 'CurrentStockLevel',
                'value': product_details['CrntStock']
            })

        return additional_properties

    def review_count(self, response):
        count = response.css('#span_rating::text').re_first('\d+')
        return int(count) if count else 0

    def best_rating(self, response):
        stars_css = '.div-rating-count .rating-block.B13_42::text'
        best = [c.strip() for c in response.css(stars_css).extract() if c.strip()]
        return float(max(best)) if best else 0.0

    def rating(self, response, product):
        best_rating = product['BestRating']
        if not best_rating:
            return {}

        ratings = response.css('.rtxt.lft::text').extract()
        if not int(best_rating) == len(ratings):
            LOGGER.error(f"Rating Scriteria doesnot match crawler needs rewrite")

        if not ratings:
            return {
                'Rating1': 0,
                'Rating2': 0,
                'Rating3': 0,
                'Rating4': 0,
                'Rating5': 0
            }

        return {
            'Rating1': int(ratings[4]),
            'Rating2': int(ratings[3]),
            'Rating3': int(ratings[2]),
            'Rating4': int(ratings[1]),
            'Rating5': int(ratings[0])
        }


class FirstCrySpiderOld(CrawlSpider):
    name = "firstcryold"
    firstcry_product = FirstCryProduct()
    start_urls = []
    file_name = '/Users/umerfarooq/Documents/Freelancing/Scrapping/2020/AbdullahBaig-firstcry/catalogue-categories-v1 - FirstCry.csv'
    listing_url_t = 'https://www.firstcry.ae/api/productfilter.svc/getsubcategorywisepagingproducts?' \
                    'pageno={}&pagesize=20&sortexpression=Popularity&subcatid={}&catid={}&ln=en'

    item_url_t = 'https://www.firstcry.ae/{}/{}/{}/product-detail'
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'RETRY_TIMES': 15,
        'URLLENGTH_LIMIT': 8000,
        'LOG_STDOUT': False,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
    }

    def __init__(self, reviews='False', short_scraper="False", *args, **kwargs):
        self.reviews = reviews.lower() == 'true'
        self.short_scraper = short_scraper.lower() == 'true'
        catalogue_url = CATALOGUE_URL_T.format(self.name, self.short_scraper)
        categories_url = "{}{}".format(HOST, catalogue_url)
        raw_res = requests.get(categories_url).json()
        self.categories = raw_res.get('data', [])
        self.vendor_code = raw_res.get('VendorCode')

    def start_requests(self):
        # with open(self.file_name, newline='') as csvfile:
        #     spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        #     for row in spamreader:
        #         url = row[2]
        #         if url:
        #             url = url.replace('"', '')
        #             yield Request(url, callback=self.parse_listing)

        for category in self.categories:
            for multi_cat in category['CategoryLink'].split(','):
                multi_cat = multi_cat.replace('"', '').replace("'", "")

                meta = {
                    'category': category,
                    'link': multi_cat,
                }

                yield Request(
                    url=multi_cat,
                    callback=self.parse_listing,
                    meta=meta.copy()
                )

    def parse_listing(self, response):

        cat_id = response.css('input#catid::attr(value)').extract_first()
        sub_cat_id = response.css('input#subcatid::attr(value)').extract_first()

        pagination_url = self.listing_url_t.format(1, sub_cat_id, cat_id)
        yield Request(pagination_url, callback=self.parse_api_categories, meta=response.meta.copy())

    def parse_api_categories(self, response):
        if response.status == 409:
            return

        yield from self.parse_sub_categories(response)

        parsed = urlparse.urlparse(response.url)
        next_pageno = int(parse_qs(parsed.query)['pageno'][0]) + 1
        pagination_url = w3lib.url.add_or_replace_parameter(response.url, 'pageno', next_pageno)
        print(f"{pagination_url}")
        yield Request(pagination_url, callback=self.parse_api_categories, meta=response.meta.copy())

    def parse_sub_categories(self, response):
        meta = response.meta.copy()
        meta['vendor_code'] = self.vendor_code
        listings = json.loads(response.text)
        for product in json.loads(listings['ProductResponse'])['Products']:
            brand = product['BNm'].replace(' ', '-')
            name = product['PNm'].lower().replace(' -', '').replace(' ', '-')
            pid = product['PInfId']
            meta['product_details'] = product
            yield Request(self.item_url_t.format(brand, name, pid), meta=meta,
                          callback=self.firstcry_product.parse_item)
