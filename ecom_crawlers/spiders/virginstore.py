import re
import json
from datetime import datetime
from urllib.parse import *

import requests
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
from ..settings import HOST, CATALOGUE_URL_T
from ecom_crawlers.utils import *


class VirginStoreSider(CrawlSpider):
    name = 'virginstore'
    headers = {
        'content-type': 'application/json',
    }
    custom_settings = {
        'DOWNLOAD_DELAY': 0.75,
        'LOG_STDOUT': False,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
    }

    test_shelve_only = False
    test_urls = [
       "https://www.virginmegastore.ae/en/gaming/playstation/playstation-games/wwe-2k20---deluxe-edition---ps4/p/780087"
        ]

    rating_url_t = 'https://d1le22hyhj2ui8.cloudfront.net/onpage/virginmegastore.ae/reviews.json?key={}'
    domain_url = 'https://www.virginmegastore.ae/{}'

    def __init__(self, reviews='False', short_scraper="False", *args, **kwargs):
        self.reviews = reviews.lower() == 'true'
        self.short_scraper = short_scraper.lower() == 'true'
        catalogue_url = CATALOGUE_URL_T.format(self.name, self.short_scraper)
        categories_url = "{}{}".format(HOST, catalogue_url)
        raw_res = requests.get(categories_url).json()
        self.categories = raw_res.get('data', [])
        self.vendor_code = raw_res.get('VendorCode')

    def start_requests(self):
        if self.test_shelve_only:
            for url in self.test_urls:
                # yield Request(url, callback=self.parse_product_links)
                yield Request(url, callback=self.parse_product)
            return

        for category in self.categories:
            for multi_cat in category['CategoryLink'].split(','):
                meta = {
                    'category': category,
                    'link': multi_cat,
                }
                yield Request(
                    url=unquote(multi_cat),
                    headers=self.headers,
                    dont_filter=True,
                    meta=meta.copy()
                    )

    def parse(self, response):
    # def parse1(self, response):
        meta = response.meta.copy()
        yield self.pagination(response, meta)
        for url in response.css('.product-list__name::attr(href)').extract():
            request = Request(unquote(response.urljoin(url)),
                              callback=self.parse_product,
                              meta=meta.copy())
            yield request

    def pagination(self, response, meta):
        next_url = response.xpath("//ul[@class='pagination-wrapper']/li/a[@rel='next']/@href").extract_first()
        total_products = clean_val(response.css('.count.mr-auto ::text').get()) or '0'

        if next_url:
            print(f"Page-{next_url[-1]}-{meta.get('category').get('CategoryName')}-{unquote(meta.get('category').get('CategoryLink'))}")
            request = Request(unquote(response.urljoin(next_url)),
                              meta=meta.copy())
            return request

        print(f"Page-1-{meta.get('category').get('CategoryName')}-{unquote(meta.get('category').get('CategoryLink'))}")

    def get_specifications(self, specification_sels):
        additional_properties = []
        for sel in specification_sels:
            for inner_sel in sel.css('tr'):
                raw_val = inner_sel.css('td::Text').extract()
                additional_properties.append({
                    'name': clean_val(raw_val[0]),
                    'value': clean_val(raw_val[1])
                })
        return additional_properties

    def get_stock_availability(self, response):
        availability = response.css('.container.page-productDetails .page-productDetails__button-add-to-cart ::Text').get()
        availability = availability.lower() if availability else ''
        if 'out of stock' in availability:
            return False
        elif 'unavailable online' in availability:
            return False
        return True

    def parse_product(self, response):
    # def parse(self, response):
        item = dict()

        category = response.meta.get('category')
        if not (self.test_shelve_only):
            item['VendorCode'] = self.vendor_code
            item['CatalogueCode'] = category['CatalogueCode']
            item['CategoryCode'] = category['CategoryCode']

        breadcrumbs = response.css('.breadcrumb-list a::Text').extract()
        item['CatalogueName'] = breadcrumbs[1]
        item['CategoryName'] = breadcrumbs[-1]

        item['ProductName'] = response.css('.title h1::text').get()
        item['URL'] = response.url
        item['SKU'] = response.url.split('/')[-1]
        item['BrandName'] = response.css('.brand a::text').get()
        if not item['BrandName']:
            raw_brand = re.findall("'brand':\s+\'(.*)\',", response.text)
            item['BrandName'] = raw_brand[0] or 'N/A' if raw_brand else 'N/A'

        item['ProductDesc'] = " | ".join(response.css('.longDesc ::text').extract())
        item['AdditionalProperty'] = self.get_specifications(response.css('.product-classifications table'))

        images = response.css('.pdp_image-carousel-image::attr(style)').re('background: url\(\\\'(.*)\\\'\)')
        item['MainImage'] = self.domain_url.format(images[0])
        item['images'] = [self.domain_url.format(image) for image in images]
        item.get('images').remove(item['MainImage'])

        model_name = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model name']
        model_name = model_name[0] if model_name else None
        item['ModelName'] = model_name

        model_number = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model number']
        model_number = model_number[0] if model_number else None
        item['ModelNumber'] = model_number

        item['StockAvailability'] = self.get_stock_availability(response)
        item['Offer'] = clean_money_str('')
        item['RegularPrice'] = clean_money_str(response.css('.container.page-productDetails .price__number::text').get())
        if response.css('.container.page-productDetails .price__number.price__number--strike-through::text').get():
            item['Offer'] = clean_money_str(response.css('.container.page-productDetails .price__number::text').get())
            item['RegularPrice'] = clean_money_str(response.css('.container.page-productDetails .price__number.price__number--strike-through::text').get())

        return Request(
            self.rating_url_t.format(item['SKU']),
            self.parse_rating,
            headers=self.headers,
            meta={'item': item.copy()}
        )

    def parse_rating(self, response):
        item = response.meta.get('item')
        item['reviews'] = list()
        item['Rating'] = dict()
        raw_reviews = json.loads(response.text)
        rating = raw_reviews.get('score')
        if not rating:
            item['RatingValue'] = 0
            item['BestRating'] = 0
            item['ReviewCount'] = 0
            return item

        reviews = [x+y for x, y in zip(raw_reviews.get('pro_score_dist_all'), raw_reviews.get('user_score_dist_all'))]
        for i, review in enumerate(reviews):
            item['Rating'][f"Rating{i+1}"] = review

        is_review_count = raw_reviews.get('pro_review_count', 0) + raw_reviews.get('user_review_count', 0) # sum of reviews (comments)
        review_count = sum(reviews)
        best_rating = reviews.index(max(reviews)) + 1
        rating = round(rating / 2.0, 2)

        item['RatingValue'] = rating
        item['BestRating'] = best_rating
        item['ReviewCount'] = review_count

        return item
