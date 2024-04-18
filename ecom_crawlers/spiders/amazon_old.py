# -*- coding: utf-8 -*-
import json
import re
from datetime import datetime
from urllib.parse import urlencode, quote_plus, unquote
import js2xml
from w3lib.url import url_query_cleaner
from math import ceil, floor
import requests
from scrapy import Spider, Request, Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse
import collections
from ..settings import HOST, CATALOGUE_URL_T
import logging

from ..settings import ITEM_PIPELINES, DOWNLOADER_MIDDLEWARES
from ecom_crawlers.utils import *


class AmazonSpiderOld(CrawlSpider):
    name = 'amazon-old'
    test_shelve_only = False
    test_urls = [
        # "https://www.amazon.ae/s?k=mobile+phones&i=electronics&rh=n%3A11601326031%2Cn%3A12303750031%2Cn%3A15415001031&dc&crid=3ND4YUVGTW137&qid=1593461551&rnid=11601327031&sprefix=mobile+%2Caps%2C155&ref=sr_nr_n_1",
        "https://www.amazon.ae/%D9%87%D8%A7%D8%AA%D9%81-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%D8%AC-%D8%AC%D8%A7%D9%84%D9%83%D8%B3%D9%8A-%D8%A7%D9%84%D8%B0%D9%83%D9%8A-%D8%A7%D8%B2%D8%B1%D9%82/dp/B084XP4LXB/ref=sr_1_1?crid=3ND4YUVGTW137&dchild=1&keywords=mobile+phones&qid=1593461551&rnid=11601327031&s=electronics&sprefix=mobile+%2Caps%2C155&sr=1-1"
        # "https://www.amazon.ae/Huawei-Y5-lite-Dual-SIM/dp/B07NF7V7YW/ref=sr_1_159?crid=3ND4YUVGTW137&dchild=1&keywords=mobile+phones&qid=1593548730&rnid=11601327031&s=electronics&sprefix=mobile+%2Caps%2C155&sr=1-159"
    ]
    review_url = 'https://www.amazon.ae/review/widgets/average-customer-review/popover/ref=acr_dpproductdetail_popover?ie=UTF8&asin={}&contextId=dpProductDetail'
    # logging.getLogger().addHandler(logging.StreamHandler())

    start_urls = [
        'https://www.amazon.ae/s?k=mobile+phones&i=electronics&rh=n%3A11601326031%2Cn%3A12303750031%2Cn%3A15415001031&dc&crid=3ND4YUVGTW137&qid=1593461551&rnid=11601327031&sprefix=mobile+%2Caps%2C155&ref=sr_nr_n_1'
        # 'https://www.amazon.ae/s?k=Laptops&i=electronics&rh=n%3A11601326031%2Cn%3A12050245031&dc&qid=1593461645&rnid=11601327031&ref=sr_nr_n_1',
    ]
    seen_ids = []

    # rating_url_t = "https://d1le22hyhj2ui8.cloudfront.net/onpage/jumbo.ae/reviews.json?url_key={}"

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'RETRY_TIMES': 15,
        'URLLENGTH_LIMIT': 8000,
        'LOG_STDOUT': False,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        'DOWNLOADER_MIDDLEWARES': {'ecom_crawlers.middlewares.UserAgentMiddleware': 350}
    }
    custom_settings['DOWNLOADER_MIDDLEWARES'].update(DOWNLOADER_MIDDLEWARES)

    def __init__(self, reviews='False', short_scraper="False", *args, **kwargs):
        super().__init__()

        self.reviews = reviews.lower() == 'true'
        self.short_scraper = short_scraper.lower() == 'true'
        catalogue_url = CATALOGUE_URL_T.format(self.name, self.short_scraper)
        categories_url = "{}{}".format(HOST, catalogue_url)
        raw_res = requests.get(categories_url).json()
        self.categories = raw_res.get('data', [])
        self.vendor_code = raw_res.get('VendorCode')
        print("############################")

    product_css = [
        '[data-component-type="s-product-image"]',
    ]
    pagination_css = ['.a-pagination .a-last, .a-pagination .a-selected + .a-normal']

    def clean_url(url):
        url = url_query_cleaner(url)
        return url.split('ref=')[0]

    def format_urls(url):
        print(url)
        return url_query_cleaner(url, parameterlist=['pf_rd_r', 'ref'], remove=True)

    rules = [
        Rule(LinkExtractor(restrict_css=pagination_css, process_value=format_urls), callback='parse_pagination'),
        Rule(LinkExtractor(restrict_css=product_css, process_value=clean_url), callback='parse_product'),
    ]

    def parse_pagination(self, response):
        print("Inside parse_pagination")
        if response.css('[data-component-type="s-product-image"]'):
            print("Parsing products...")
            yield from self.parse(response)
        else:
            print("Retrying request due to captcha...")
            yield from self.retry_request(response)

    def retry_request(self, response):
        print("Inside retry_request")
        retry = response.meta.get('retry')
        if retry and retry > 2:
            self.logger.info("Ignoring Url {}".format(response.url))
        else:
            self.logger.info("Captcha Found Url {}".format(response.url))
            meta = response.meta.copy()
            meta['retry'] = retry + 1 if retry else 1
            return Request(response.url, dont_filter=True, meta=meta, callback=response.request.callback)

    def clean(self, str_or_lst):
        if str_or_lst is None:
            return
        if not isinstance(str_or_lst, str) and getattr(str_or_lst, '__iter__', False):
            return [j for j in (self._clean_val(i) for i in str_or_lst if i is not None) if j]
        return self._clean_val(str_or_lst)

    def _clean_val(self, val):
        return re.sub('\s+', ' ', val.replace('\xa0', ' ')).strip()

    def parse(self, response):
        print("Inside parse")
        print("Parsing response:", response.url)
        for request in super(AmazonSpider, self).parse(response):
            if isinstance(request, Request):
                merged_meta = {**response.meta, **request.meta}
                request = request.replace(meta=merged_meta.copy())

                yield request

    def start_requests(self):
        print("Starting requests...")
        if self.test_shelve_only:
            for url in self.test_urls:
                print("Test URL:", url)
                yield Request(url)
            return

        for category in self.categories:
            for multi_cat in category['CategoryLink'].split(','):
                meta = {
                    'category': category,
                    'link': multi_cat,
                }
                print("Category: ", category)
                print("Link: ", multi_cat)
                yield Request(
                    url=multi_cat,
                    callback=self.parse,
                    meta=meta.copy()
                )

    def fetch_additional_property(self, sels):
        print("Inside fetch_additional_property")
        if not sels:
            return []

        raw_additional_pr = []
        for sub_sel in sels:
            for sel in sub_sel.css('tr'):
                key_val = sel.css('td::Text').extract()
                if self.clean(key_val[0]) and self.clean(key_val[0]).lower() != 'customer reviews':
                    raw_additional_pr.append({
                        'name': self.clean(key_val[0]),
                        'value': self.clean(key_val[1]) if len(key_val) == 2 else 'N/A'
                    })
        return raw_additional_pr

    def get_stock_availability(self, response):
        print("Inside get_stock_availability909")
        # return True if response.css('#availabilityInsideBuyBox_feature_div') else False
        availability = [item.lower() for item in self.clean(response.css('#availabilityInsideBuyBox_feature_div ::Text').extract())]
        available = 'in stock.' in availability or 'add to cart' in availability
        return available

    def parse_category(self, response, item):
        print("Inside parse_category")
        raw_cats = self.clean(response.css('.a-breadcrumb .a-list-item a::text').getall())
        if raw_cats:
            item['CatalogueName'] = raw_cats[1]
            item['CategoryName'] = raw_cats[-1]

    def brand_name(self, response):
        print("Inside brand_name")
        brand = response.css('#mbc::attr(data-brand)').get()
        return brand if brand else self.clean(response.css('#bylineInfo::text').get())

    # def parse_prices(self, response, item):
    #     item['RegularPrice'] = clean_money_str(
    #         response.css('.priceBlockBuyingPriceString::text').get().split(' -')[0])
    #     item['RegularPrice'] = clean_money_str(response.css('.priceBlockBuyingPriceString::text').get())
    #     disc_price = response.css('.priceBlockStrikePriceString::text').get()
    #     item['Offer'] = clean_money_str('')
    #     if disc_price:
    #         item['Offer'] = item['RegularPrice']
    #         item['RegularPrice'] = clean_money_str(disc_price)
    #
    #     if not item['RegularPrice']:
    #         price = self.clean(response.xpath('(//*[@class="a-color-price"])[1]//text()').get())
    #         item['RegularPrice'] = clean_money_str(price)
    #
    #     if not item['RegularPrice']:
    #         item['RegularPrice'] = clean_money_str(
    #             response.css('.priceBlockBuyingPriceString::text').get().split(' -')[0]
    #         )

    def parse_prices(self, response, item):
        print("Inside parse_prices")
        item['RegularPrice'] = clean_money_str(
            response.css('.priceBlockBuyingPriceString::text').get().split(' -')[0])
        disc_price = response.css('.priceBlockStrikePriceString::text').get()
        if disc_price:
            item['Offer'] = item['RegularPrice']
            item['RegularPrice'] = clean_money_str(disc_price)

        if not item['RegularPrice']:
            price = self.clean(response.xpath('(//*[@class="a-color-price"])[1]//text()').get())
            item['RegularPrice'] = clean_money_str(price)

        if not item.get('Offer'):
            item['Offer'] = format(0.0, '.2f')

        print("Parsed prices: RegularPrice:", item['RegularPrice'], "Offer:", item.get('Offer'))

    def parse_images(self, response, item):
        print("Inside parse_images")
        raw_images = response.xpath("//script[contains(text(), 'register(\"ImageBlockATF\"')]/text()").re("initial'\s*:\s*(\[.*\])},")
        if raw_images:
            raw_images = json.loads(raw_images[0])
            images = [img.get('hiRes') or img.get('large') for img in raw_images]
            item['MainImage'] = images[0] if images else ''
            item['images'] = images
            if item['MainImage']:
                item.get('images').remove(item['MainImage'])
            return
        raw_images = response.xpath("//script[contains(text(), 'register(\"ImageBlockATF\"')]/text()").re("imageGalleryData'\s*:\s*(\[.*\]),")
        if raw_images:
            raw_images = json.loads(raw_images[0])
            images = [img.get('mainUrl') for img in raw_images]
            item['MainImage'] = images[0] if images else ''
            item['images'] = images
            if item['MainImage']:
                item.get('images').remove(item['MainImage'])

        print("Parsed images:", item['MainImage'], item['images'])

    def parse_review_rating(self, response, item):
        print("Inside parse_review_rating")
        item['Rating'] = dict()
        raw_avg_rating = response.css("#reviewsMedley").xpath(
            '//span[contains(@data-hook, "rating-out-of-text")]//text()').get()
        raw_total_ratings = response.css('#acrCustomerReviewText::Text').get()

        if not raw_total_ratings:
            item['RatingValue'] = 0
            item['BestRating'] = 0
            item['ReviewCount'] = 0
            return True
        if raw_total_ratings and not raw_avg_rating:
            return False

        item['RatingValue'] = float(raw_avg_rating.split(" ")[0])
        item['ReviewCount'] = int(raw_total_ratings.split(" ")[0])

        raw_review_sels = response.css('#histogramTable .a-histogram-row')
        ratings = dict()
        total_percent = 0
        for sel in raw_review_sels:
            review = self.clean(sel.css('.a-size-base ::text').getall())
            percent = int(review[1].split("%")[0])
            total_percent += percent
            rating_count = ceil((lambda x, y: x * y / 100.0)(percent, item['ReviewCount']))
            star = int(review[0].split(' ')[0])
            ratings[star] = rating_count
            item['Rating'][f"Rating{star}"] = rating_count

        if not total_percent:
            return False

        ratings = collections.OrderedDict(sorted(ratings.items()))
        max_rating = max(ratings, key=int) if ratings else 0.0
        item['BestRating'] = max_rating
        return True

    def parse_request_reveiw(self, response):
        print("Inside parse_request_reveiw")
        item = response.meta.get('item')
        total_rating = int(response.css('.totalRatingCount::text').get().split(' ')[0])
        if not total_rating:
            return

        item['ReviewCount'] = total_rating
        item['RatingValue'] = response.css('[data-hook="acr-average-stars-rating-text"]::text').get().split(' ')[0]
        raw_review_sels = response.css('#histogramTable .a-histogram-row')
        ratings = dict()

        for sel in raw_review_sels:
            review = self.clean(sel.css('.a-size-base ::text').getall())
            percent = int(review[1].split("%")[0])
            rating_count = ceil((lambda x, y: x * y / 100.0)(percent, item['ReviewCount']))
            star = int(review[0].split(' ')[0])
            ratings[star] = rating_count
            item['Rating'][f"Rating{star}"] = rating_count

        ratings = collections.OrderedDict(sorted(ratings.items()))
        max_rating = max(ratings, key=int) if ratings else 0.0
        item['BestRating'] = max_rating

        print("Parsed review rating:", item)
        return item

    def get_model_number(self, response, item):
        print("Inside get_model_number")
        model_number = response.css('.item-model-number .value::text, li:contains("model number")::text').get()
        if not model_number:
            model_number = [mn['value'] for mn in item['AdditionalProperty'] if
                            mn['name'].lower() == 'item model number']
            model_number = model_number[0] if model_number else None
        return model_number

    def product_asin(self, response):
        print("Inside product_asin")
        asin = self.clean(response.css('#cerberus-data-metrics::attr(data-asin)').get())
        if asin:
            return asin

        asin = self.clean(response.css("#twisterNonJsData [name='ASIN']::attr(value)"))
        return asin[0] if asin else response.url.split('/dp/')[-1].split('?')[0].split('/')[0]

    def parse_product(self, response):
        print("Inside parse_product")
        item = dict()
        category = response.meta.get('category')
        if not self.test_shelve_only:
            item['VendorCode'] = self.vendor_code
            item['CatalogueCode'] = category['CatalogueCode']
            item['CategoryCode'] = category['CategoryCode']

        self.parse_category(response, item)

        item['SKU'] = self.product_asin(response).replace('/', '')

        if item['SKU'] in self.seen_ids:
            return
        self.seen_ids.append(item['SKU'])
        item['URL'] = response.url
        
        print("Before setting ProductName")
        item['ProductName'] = self.clean(response.css('#productTitle::Text').get())
        print("After setting ProductName:", item['ProductName'])
        if item['ProductName'] is None:
            print("Product name is None, retrying request...")
            return self.retry_request(response)

        print("Before setting BrandName")
        item['BrandName'] = self.brand_name(response) or 'N/A'
        print("After setting BrandName:", item['BrandName'])

        desc_css = ['#productDescription ::Text', '#featurebullets_feature_div :not(script)::text']
        # item['ProductDesc'] = " | ".join(self.clean(response.css('#productDescription ::Text').extract())).replace('Product Description |', '')
        # if not item['ProductDesc']:
        item['ProductDesc'] = " | ".join(self.clean(response.css(','.join(desc_css)).extract())).replace('Product Description |', '')
        print("ProductDesc:", item['ProductDesc'])

        print("Before fetching additional properties")
        item['AdditionalProperty'] = self.fetch_additional_property(response.css('.pdTab table'))
        print("After fetching additional properties:", item['AdditionalProperty'])

        model_name = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model name']
        model_name = model_name[0] if model_name else None
        item['ModelName'] = model_name

        print("Before getting ModelNumber")
        item['ModelNumber'] = self.get_model_number(response, item)
        print("After getting ModelNumber:", item['ModelNumber'])

        print("StockAvailability determination")
        item['StockAvailability'] = self.get_stock_availability(response)
        print("StockAvailability:", item['StockAvailability'])

        print("Parsing images")
        self.parse_images(response, item)
        print("MainImage:", item['MainImage'])
        print("Images:", item['images'])

        print("Parsing prices")
        self.parse_prices(response, item)
        print("RegularPrice:", item['RegularPrice'])
        print("Offer:", item.get('Offer'))

        print("Parsing review rating")
        is_review = self.parse_review_rating(response, item)
        print("Is review:", is_review)

        if is_review:
            return item

        return Request(self.review_url.format(item['SKU']), meta={'item': item}, callback=self.parse_request_reveiw)
