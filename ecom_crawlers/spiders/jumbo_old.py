# -*- coding: utf-8 -*-
import json
import re
from datetime import datetime
from urllib.parse import urlencode, quote_plus, unquote

import requests
from scrapy import Spider, Request
from scrapy.http import HtmlResponse
from ecom_crawlers.utils import *

from ..settings import HOST, CATALOGUE_URL_T


class JumboSpiderOld(Spider):
    name = 'jumbo_old'
    headers = {
        'content-type': 'application/json',
    }
    test_shelve_only = False
    test_urls = [
       # "https://www.jumbo.ae/mobile-phones/",
       #  "https://www.jumbo.ae/smart-phones/huawei-p40-pro-smartphone-5g/p-0441617-34166160249-cat.html",
       #  "https://www.jumbo.ae/smart-phones/samsung-galaxy-z-flip-smartphone-lte/p-0441617-30444102098-cat.html",
       #  "https://www.jumbo.ae/ihealth-edge-activity-sleep-tracker-fitness-wearable-devices-AM3S.html#variant_id=0441617-88941414461",
       #  "https://www.jumbo.ae/wearable-accessories/behello-premium-apple-watch-silicone-strap-38-40mm/p-0441617-63325430809-cat.html#variant_id=0441617-63325430809"
        # "https://www.jumbo.ae/mobile-phones/smart-phones",
        # "https://www.jumbo.ae/computers/laptops",
        # "https://www.jumbo.ae/cameras/mirrorless-cameras",
        # "https://www.jumbo.ae/wearables#/?br_nodes[]=ho67760027_wear_smar&_xhr=1",
        # "https://www.jumbo.ae/televisions/LED-Televisions"
        ]

    rating_url_t = "https://d1le22hyhj2ui8.cloudfront.net/onpage/jumbo.ae/reviews.json?url_key={}"

    custom_settings = {
        'DOWNLOAD_DELAY': 0.90,
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

    def filter_list(self, descriptions):
        raw_description = [clean_val(description) for description in descriptions]
        return list(filter(None, raw_description))

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
                    url=multi_cat,
                    callback=self.parse_product_links,
                    meta=meta.copy()
                )

    def parse_product_links(self, response):
    # def parse(self, response):
        meta = response.meta.copy()
        total_items = re.findall("Of\s(.*)?\sResults", clean_val(response.css('.bn-message ::text').get()))[0]
        for product_url in response.css('#search-result-items .variant-title a::attr(href)').extract():
            yield Request(response.urljoin(product_url),
                          callback=self.parse_product,
                          meta=meta)
        page_num = "1"
        if re.findall('\?page=([\d+])?|&', response.url):
            page_num = re.findall('\?page=([\d+])?|&', response.url)[0]

        print(f"{page_num}-{total_items}-{response.url}")
        next_page_url = response.css('.next_page::attr(href)').get()
        if next_page_url:
            yield Request(response.urljoin(next_page_url),
                          callback=self.parse_product_links,
                          meta=meta)

    def fetch_additional_property(self, sels):
        raw_additional_pr = []
        if sels:
            for sub_sel in sels:
                for sel in sub_sel.css('tr'):
                    key_val = sel.css('td::Text').extract()

                    raw_additional_pr.append({
                        'name': clean_val(key_val[0]),
                        'value': clean_val(key_val[1]) if len(key_val) == 2 else 'N/A'
                    })
        return raw_additional_pr

    def get_stock_availability(self, response):
        availability = [item.lower() for item in response.css('.in-stock span::Text').extract()]
        available = 'in stock' in availability
        if not available:
            raw_available = [item.lower() for item in response.css(".add-to-cart::Attr(value)").extract()]
            available = 'add to cart' in raw_available
        return available

    def parse_product(self, response):
    # def parse(self, response):

        item = dict()
        category = response.meta.get('category')
        if not(self.test_shelve_only):
            item['VendorCode'] = self.vendor_code
            item['CatalogueCode'] = category['CatalogueCode']
            item['CategoryCode'] = category['CategoryCode']

        raw_breadcrumbs = response.css('.bread-crumbs span::Text').extract()
        item['CatalogueName'] = raw_breadcrumbs[1]
        item['CategoryName'] = raw_breadcrumbs[-1]

        item['URL'] = response.url
        item['ProductName'] = response.css('#title h1::text').get()
        item['BrandName'] = clean_val(response.css('#brand_name::text').get()) or 'N/A'
        item['SKU'] = response.css('#item_sku::text').get()

        item['ModelNumber'] = 'N/A'
        images = response.css("#images a::attr(data-medium-url)").extract()
        item['MainImage'] = response.css('.var-img-slider img::attr(src)').get()
        item['images'] = images
        if item['MainImage']:
            item.get('images').remove(item['MainImage'])

        item['ProductDesc'] = " | ".join(self.filter_list(response.css('#description-text ::Text').extract()))

        item['AdditionalProperty'] = self.fetch_additional_property(response.css('#feature_groups table'))

        model_name = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model name']
        model_name = model_name[0] if model_name else None
        item['ModelName'] = model_name

        if not item['ModelNumber']:
            model_number = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model number']
            model_number = model_number[0] if model_number else None
            item['ModelNumber'] = model_number

        item['StockAvailability'] = self.get_stock_availability(response)
        item['RegularPrice'] = clean_money_str(response.css('.our_price .m-w::Text').get())
        item['Offer'] = clean_money_str('')

        if response.css('#pricing_summary .list_price.strike span.m-w::Text').get():
            item['Offer'] = item['RegularPrice']
            item['RegularPrice'] = clean_money_str(response.css('#pricing_summary .list_price.strike span.m-w::Text').get())

        product_id = ''
        id = re.findall("/p-(.*)?-cat.html", response.url)
        if id:
            product_id = id[0]
        else:
            var_id = re.findall('#variant_id=(.*)?|&', response.request.url)
            if var_id:
                product_id = var_id[0]

        if product_id:
            return Request(
                self.rating_url_t.format(product_id),
                self.parse_rating,
                headers=self.headers,
                meta={'item': item.copy()}
            )

    def parse_rating(self, response):
        item = response.meta.get('item')
        item['reviews'] = list()
        item['Rating'] = dict()
        # raw_reviews = json.loads(re.findall("testFreaks.cb\((.*)\)", response.text)[0])
        raw_reviews = json.loads(response.text)
        rating = raw_reviews.get('score')
        if not rating:
            item['RatingValue'] = 0
            item['BestRating'] = 0
            item['ReviewCount'] = 0
            return item

        reviews = []
        if raw_reviews.get('your_score_dist'):
            reviews = raw_reviews.get('your_score_dist')

        if raw_reviews.get('user_score_dist_all') and \
                raw_reviews.get('pro_score_dist_all'):
            reviews = [x + y for x, y in
                       zip(raw_reviews.get('pro_score_dist_all'),
                           raw_reviews.get('user_score_dist_all'))]
        if raw_reviews.get('your_score_dist') and \
                raw_reviews.get('user_score_dist_all') and \
                raw_reviews.get('pro_score_dist_all'):
            reviews = [x + y + z for x, y, z in
                       zip(raw_reviews.get('pro_score_dist_all'),
                           raw_reviews.get('user_score_dist_all'),
                           raw_reviews.get('your_score_dist'))]

        for i, review in enumerate(reviews):
            item['Rating'][f"Rating{i + 1}"] = review

        is_review_count = raw_reviews.get('pro_review_count', 0) + raw_reviews.get('user_review_count',
                                                                                   0)  # sum of reviews (comments)
        review_count = sum(reviews)
        best_rating = reviews.index(max(reviews)) + 1
        rating = round(rating / 2.0, 2)

        item['RatingValue'] = rating
        item['BestRating'] = best_rating
        item['ReviewCount'] = review_count

        return item

