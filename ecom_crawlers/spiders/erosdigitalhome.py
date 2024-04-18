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


class ErosDigitalHomeSpider(Spider):
    name = 'erosdigitalhome'
    headers = {
        'content-type': 'application/json',
    }
    test_shelve_only = False
    test_urls = [
            # "https://www.erosdigitalhome.ae/smart-phones.html",
        # "https://www.erosdigitalhome.ae/huawei-nova-7i-6-4-inch-128gb-8gb-48mp-quad-ai-cameras-smartphone.html"
        # "https://www.erosdigitalhome.ae/samsung-galaxy-s20-plus-5g-6-7inch-hybrid-esim-smartphone.html#e_var_color=69&e_var_capacity=538",
        # 'https://www.erosdigitalhome.ae/catalogsearch/result/index/?product_brand=Lenovo&q=All+In+One+Desktop&p=1',
        # 'https://www.erosdigitalhome.ae/tv-audio-video/television.html',
        # 'https://www.erosdigitalhome.ae/samsung-galaxy-fold-7-3-inch-dynamic-amoled-display-512-gb-12-gb-ram.html#e_var_color=545&e_var_capacity=956',
        # 'https://www.erosdigitalhome.ae/samsung-galaxy-s20-plus-5g-6-7inch-hybrid-esim-smartphone.html#e_var_color=68&e_var_capacity=538',
        # 'https://www.erosdigitalhome.ae/be-light-table-black-warm-white-6282333.html',
        # 'https://www.erosdigitalhome.ae/sonos-move-portable-smart-wireless-speaker.html',
        # 'https://www.erosdigitalhome.ae/tucano-forte-backpack-in-nylon-for-notebook-15-6-inch.html',
        # 'https://www.erosdigitalhome.ae/huawei-y8p-6-3-inches-128gb-6gb-4000mah-smartphone-midnight-black-color.html'
        'https://www.erosdigitalhome.ae/samsung-65-inch-class-q900-qled-smart-8k-uhd-tv-2019.html'
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
                # yield Request(url, callback=self.parse_product_links)
                yield Request(url, callback=self.parse_product)
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
        for product_url in response.css('.product-item .product-image a::attr(href)').extract():
            yield Request(product_url,
                          callback=self.parse_product,
                          meta=meta)

        if '?' in response.url and "p=" in response.url:
            page_num = re.findall('p=([\d]+)?', response.url)[0]
            p_num = f"p={int(page_num) + 1}"
            next_page_url = re.sub('p=([\d]+)?', p_num, response.url)
        elif '?' in response.url and "p=" not in response.url:
            next_page_url = f"{response.url}&p=1"
        elif '?' not in response.url and "p=" not in response.url:
            next_page_url = f"{response.url}?p=1"

        print(f"{total_items}-{next_page_url}")
        if total_items:
            yield Request(next_page_url,
                          callback=self.parse_product_links,
                          meta=meta)

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
        availability = [item.lower() for item in response.css('.stock span::text').extract()]
        available = 'in stock' in availability
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
        raw_breadcrumbs = self.filter_list(response.css('.breadcrumbs .items li ::text').extract())
        item['CatalogueName'] = raw_breadcrumbs[0]
        item['CategoryName'] = raw_breadcrumbs[-1]

        item['URL'] = response.url
        item['ProductName'] = response.css('.page-title span::text').get()
        brand_name = response.css('.pdp_brand_notimer img::attr(src)').re('brands\/(.*)?.png')
        item['BrandName'] = (brand_name[0] or 'N/A') if brand_name else 'N/A'

        model_number = self.filter_list(response.css('.pdp-model_number::text').extract())
        item['ModelNumber'] = model_number[0] if model_number else 'N/A'

        item['SKU'] = item['ModelNumber']

        variants = response.xpath('//script/text()[contains(.,"optionPrices")]').re('full":"(.*?)"')
        images = response.xpath('//script/text()[contains(.,"optionPrices")]').re('full":"(.*?)"') or \
                 response.xpath('//script/text()[contains(.,"magnifierOpts")]').re('full":"(.*?)"')

        images = self.clean_image_urls(images)
        item['MainImage'] = images[0] if images else 'N/A'
        item['images'] = images
        if item['MainImage']:
            item.get('images').remove(item['MainImage'])

        item['AdditionalProperty'] = self.fetch_additional_property(response.css('#product-attribute-specs-table'))
        item['ProductDesc'] = " | ".join(self.filter_list(response.css('#description-text ::Text').extract()))

        model_name = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model name']
        model_name = model_name[0] if model_name else None
        item['ModelName'] = model_name

        if not item['ModelNumber']:
            model_number = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model number']
            model_number = model_number[0] if model_number else None
            item['ModelNumber'] = model_number

        item['StockAvailability'] = self.get_stock_availability(response)

        item['Offer'] = clean_money_str('')
        if variants:
            default_variant = self.get_default_variant(response)
            item['RegularPrice'] = clean_money_str(default_variant['oldPrice']['amount'])
            item['Offer'] = clean_money_str(default_variant['finalPrice']['amount'])
        else:
            item['RegularPrice'] = clean_money_str(response.css(".product-info-price .price-final_price .price::text").get())
            if response.css('.product-info-price .special-price .price::Text').get():
                item['Offer'] = clean_money_str(response.css('.product-info-price .special-price .price::Text').get())

        item['reviews'] = list()
        item['Rating'] = dict()
        item['RatingValue'] = 0
        item['BestRating'] = 0
        item['ReviewCount'] = 0

        return item

    def get_default_variant(self, response):
        raw_variants = response.xpath('//script/text()[contains(.,"optionPrices")]').get()
        raw_variants = re.findall('jsonConfig\":\s(\{.*),', raw_variants, re.MULTILINE)
        json_variants = json.loads(raw_variants[0])
        in_stock_ids = list(json_variants['optionStocks'].values())

        return json_variants['optionPrices'][in_stock_ids[0]]