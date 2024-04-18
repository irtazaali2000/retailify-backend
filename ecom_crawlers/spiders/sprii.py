# -*- coding: utf-8 -*-
import json
import re
from datetime import datetime
from urllib.parse import urlencode, quote_plus, unquote
from math import ceil
import requests
from scrapy import Spider, Request
from scrapy.http import HtmlResponse
from ecom_crawlers.utils import *

from ..settings import HOST, CATALOGUE_URL_T


class SpriiSpider(Spider):
    name = 'sprii'
    headers = {
        'content-type': 'application/json',
    }
    test_shelve_only = False
    # test_shelve_only = True
    test_urls = [
            # "https://www.sprii.ae/en/standard/?p=1",
            # "https://www.sprii.ae/en/babyzen-stroller-yoyo-2-0-2228-bz10104-05-a-c.html",
            # "https://www.sprii.ae/en/yahababy-modern-stroller-violet.html",
        # 'https://www.sprii.ae/en/catalogsearch/result/index/?cat=993&q=Weighting+Scales'
        'https://www.sprii.ae/en/vacuum-cleaners/?price=632-8401&product_list_order=price&p=2'
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
                # if '?' in url:
                #     url = f"{url}&p=1"
                # else:
                #     url = f"{url}?p=1"
                yield Request(url, callback=self.parse_product_links)
                # yield Request(url, callback=self.parse_product)
            return

        for category in self.categories:
            for multi_cat in category['CategoryLink'].split(','):
                # if 'https://www.erosdigitalhome.ae/tv-audio-video/television.html' in multi_cat:
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
        total_items = response.css('.toolbar-number::text').get()
        total_pages = ceil(float(response.css(".toolbar-number::text").get()) / 16)
        for product_url in response.css(".product-item-photo::Attr(href)").extract():
            yield Request(product_url,
                          callback=self.parse_product,
                          meta=meta)

        next_page_url = ''
        if '?' in response.request.url and "p=" in response.request.url:
            old_page_num = re.findall('p=([\d]+)?', response.url)[0]
            page_num = int(old_page_num) + 1
            if page_num <= total_pages:
                p_num = f"p={page_num}"
                next_page_url = re.sub('p=([\d]+)?', p_num, response.url)
                yield Request(next_page_url,
                                  callback=self.parse_product_links,
                                  meta=meta)
        elif '?' in response.url and "p=" not in response.url:
            next_page_url = f"{response.url}&p=2"
            yield Request(next_page_url,
                              callback=self.parse_product_links,
                              meta=meta)
        elif '?' not in response.url and "p=" not in response.url:
            next_page_url = f"{response.url}?p=2"
            yield Request(next_page_url,
                          callback=self.parse_product_links,
                          meta=meta)

        print(f"{total_items}-{next_page_url}")


    def fetch_additional_property(self, sels):
        raw_additional_pr = []
        if sels:
            for sub_sel in sels:
                for sel in sub_sel.css('tr'):
                    key = sel.css('th::Text').get()
                    val = sel.css('td::Text').get()

                    raw_additional_pr.append({
                        'name': clean_val(key),
                        'value': clean_val(val)
                    })
        return raw_additional_pr

    def get_stock_availability(self, response):
        availability = [item.lower() for item in response.css('.product-info-price .stock span::text').extract() or
                        response.css(".box-tocart.box-tocart-dami span::Text").extract()]
        available = 'in stock' in availability or 'add to cart' in availability
        return available

    def clean_image_urls(self, images):
        return [image.replace("\\", "") for image in images]

    def parse_product(self, response):
    # def parse(self, response):

        item = dict()
        category = response.meta.get('category')
        if not(self.test_shelve_only):
            item['VendorCode'] = self.vendor_code
            item['CatalogueCode'] = category['CatalogueCode']
            item['CategoryCode'] = category['CategoryCode']
        raw_breadcrumbs = self.filter_list(response.css('.breadcrumb .item ::text').extract())
        item['CatalogueName'] = raw_breadcrumbs[2]
        item['CategoryName'] = raw_breadcrumbs[-2]

        item['URL'] = response.url
        item['ProductName'] = response.css('.page-title span::text').get()
        item['BrandName'] = response.xpath("//td[@data-th='Brand']/text()").get() or 'N/A'
        item['SKU'] = response.xpath("//td[@data-th='SKU']/text()").get()
        item['ProductDesc'] = " | ".join(self.filter_list(response.css('.product.description .value ::Text').extract()))

        images = response.xpath('//script/text()[contains(.,"magnifierOpts")]').re('full":"(.*?)"')

        images = self.clean_image_urls(images)
        item['MainImage'] = images[0] if images else 'N/A'
        item['images'] = images
        if item['MainImage']:
            item.get('images').remove(item['MainImage'])

        item['StockAvailability'] = self.get_stock_availability(response)

        item['AdditionalProperty'] = self.fetch_additional_property(response.css('#product-attribute-specs-table'))

        model_name = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model name']
        model_name = model_name[0] if model_name else None
        item['ModelName'] = model_name

        model_number = self.filter_list(response.css('.pdp-model_number::text').extract())
        item['ModelNumber'] = model_number[0] if model_number else 'N/A'

        if not item['ModelNumber']:
            model_number = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model number']
            model_number = model_number[0] if model_number else None
            item['ModelNumber'] = model_number

        item['Offer'] = clean_money_str('')
        item['RegularPrice'] = clean_money_str(response.css('.product-info-price .price-final_price .pricepart::text').get())
        if response.css('.old-price .pricepart::text').get():
            item['Offer'] = item['RegularPrice']
            item['RegularPrice'] = clean_money_str(response.css('.old-price .pricepart::text').get())

        item['reviews'] = list()
        item['Rating'] = dict()
        item['RatingValue'] = 0
        item['BestRating'] = 0
        item['ReviewCount'] = 0

        return item
