# -*- coding: utf-8 -*-
import json
import re
from datetime import datetime
from urllib.parse import urlencode, quote_plus, unquote, urlparse
import requests
from scrapy import Spider, Request
from scrapy.http import HtmlResponse
from ecom_crawlers.utils import *

from ..settings import HOST, CATALOGUE_URL_T


class MumzWorldSpider(Spider):
    name = 'mumzworld'
    ALGOLIA_KEYS = {
        'X-Algolia-API-Key': '812d659d75e6a19c71c7a7198d2dd165',
        'X-Algolia-Application-Id': '0LZ0827VB4',

    }
    ALGOLIA_BASE = "https://0lz0827vb4-dsn.algolia.net/1/indexes"
    product_per_page = 48
    rating_url_t = "https://d1le22hyhj2ui8.cloudfront.net/badge/sharafdg.com/reviews.json?key={}"
    description_url_t = "https://ws.cnetcontent.com/3f2c4539/script/45094ea3b2?cpn={sku}&mf={brand_name}&pn={model_no}"

    headers = {
        'content-type': 'application/json',
    }
    test_shelve_only = False
    test_urls = [
        # 'https://www.mumzworld.com/en/sunveno-child-face-mask-5pc-set',
        'https://www.mumzworld.com/en/fine-guard-n95-kids-and-teens-face-mask-livinguard-technology-medium-black'
        # 'https://www.mumzworld.com/en/#search=Women%20Bags&page=0&minReviewsCount=0&minPrice=0&curmaxPrice=685&refinements=%5B%7B%22categories%22%3A%22Bags%22%7D%2C%7B%22gender%22%3A%22Women%22%7D%5D'
        # 'https://www.mumzworld.com/en/nursery-bedroom/baby-furniture#search=women%20perfume&page=0&minReviewsCount=0&minPrice=0&curmaxPrice=84&refinements=%5B%7B%22categories%22%3A%22Perfumes%22%7D%5D'
        ]

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
                yield Request(url, callback=self.parse_product)
                # yield Request(url, callback=self.parse_product)
            return

        for category in self.categories:
            for multi_cat in category['CategoryLink'].split(','):
                meta = {
                    'category': category,
                    'link': multi_cat,
                }
                if '#' in  multi_cat:
                    yield Request(
                        url=multi_cat,
                        callback=self.parse_category,
                        meta=meta.copy()
                    )
                else:
                    yield Request(
                        url=multi_cat,
                        callback=self.parse_product_links_noalgo,
                        meta=meta.copy()
                    )

    def make_algolia_request(self, meta, page=0):
        post_url = "{}/*/queries?{}".format(
            self.ALGOLIA_BASE, urlencode(self.ALGOLIA_KEYS)
        )
        facet_filter = quote_plus(str(meta.get('facet_filter'))).replace('+', '%20')
        params = "query={query_param}&hitsPerPage={product_per_page}&maxValuesPerFacet=50&page={page}&facets=%5B%22price.AED%22%2C%22brand%22%2C%22gender%22%2C%22sale_item%22%2C%22collections%22%2C%22clothesage%22%2C%22age%22%2C%22category_level1_eng%22%2C%22yalla%22%5D&facetFilters={facet_filter}&numericFilters=price.AED%3E%3D0%2Cprice.AED%3C%3D{max_price}"  # NOQA
        data = {
            "requests": [
                {
                    "indexName": "eng_mumz_baby",
                    "params": params.format(
                        query_param=meta.get('query_param'),
                        page=page,
                        facet_filter=facet_filter,
                        product_per_page=self.product_per_page,
                        max_price=meta.get('max_price')
                    )
                }
            ]
        }
        json_data = json.dumps(data)
        yield Request(
            url=post_url, callback=self.parse_product_links, dont_filter=True,
            body=json_data, meta=meta.copy(), method='POST',
            # Required referer, otherwise it's got 403
            headers={'Referer': meta.get('friendly_url')}
        )

    def get_facets(self, params):
        facet = ''
        for param in params:
            if 'refinements=' in param:
                facet = re.findall("refinements=(.*)", param)[0]
        return facet.replace("{", '').replace('[', '').replace("\"", '').replace("}", '').replace(']', '')

    def get_max_price(self, params):
        max_price = ''
        for param in params:
            if 'curmaxPrice=' in param:
                max_price = re.findall("curmaxPrice=(.*)", param)[0]
        return max_price

    def parse_category(self, response):
        meta = response.meta.copy()
        param_refinement = unquote(response.request.url)
        params = urlparse(param_refinement).fragment.split('&')
        raw_cat_name = self.get_facets(params)
        facet_string = '[%s]'
        sub_facet_string = '["%s"]'
        sub_cat_name = ','.join([sub_facet_string % a for a in raw_cat_name.split(',')])
        cat_name = facet_string % sub_cat_name
        max_price = self.get_max_price(params)
        query_param = ''
        if "search=" in response.request.url:
            query_param = re.findall("search=(.*?)&", response.request.url)[0]
            self.logger.info('Query Param Found %s', query_param)

        meta['facet_filter'] = cat_name
        meta['query_param'] = query_param
        meta['friendly_url'] = response.url
        meta['max_price'] = max_price
        for req in self.make_algolia_request(meta=meta):
            yield req

    def parse_product_links_noalgo(self, response):
        meta = response.meta.copy()
        total_items = response.css('.sale_item_count::text').get()
        print(f"{total_items}-{response.url}")

        for product_url in response.css('.product-image.itemsmain::attr(href)').extract():
            yield Request(product_url,
                          callback=self.parse_product,
                          meta=meta)

        next_page_url = response.css('.i-next::attr(href)').get()
        if next_page_url:
            print(f"{total_items}-{next_page_url}")
            yield Request(next_page_url,
                          callback=self.parse_product_links_noalgo,
                          meta=meta)

    def parse_product_links(self, response):
        json_data = json.loads(response.text).get('results')[0]
        current_page = response.meta.get('page_number', 1)
        total_page = json_data.get('nbPages')
        friendly_url = response.meta.get('friendly_url')
        print(f"{current_page}-{total_page}-{friendly_url}")

        for product in json_data.get('hits'):
            meta = response.meta.copy()
            yield Request(product['url'], meta=meta.copy(), callback=self.parse_product)

        if current_page < total_page:
            meta = response.meta.copy()
            meta.update({'page_number': current_page + 1})
            for req in self.make_algolia_request(meta, page=current_page):
                yield req

    def fetch_additional_property(self, sels):
        raw_additional_pr = []
        try:
            if sels:
                for i in range(0, len(sels), 2):
                    raw_additional_pr.append({
                        'name': clean_val(sels[i]),
                        'value': clean_val(sels[i+1])
                    })
        except IndexError as e:
            pass

        return raw_additional_pr

    def get_stock_availability(self, response):
        availability = response.css(".add-to-cart button ::Text").get()
        availability = 'add to bag' in availability.lower() if availability else False
        return availability

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
        raw_breadcrumbs = self.filter_list(response.css('.breadcrumbs li ::text').extract())
        item['CatalogueName'] = raw_breadcrumbs[0]
        item['CategoryName'] = raw_breadcrumbs[-1]

        item['URL'] = response.url
        item['ProductName'] = response.css('.product-name h1::text').get()
        brand_name = response.xpath('//script/text()[contains(.,"visitorLoginState")]').re('brand":"(.*?)"')
        item['BrandName'] = (brand_name[0] or 'N/A') if brand_name else 'N/A'

        model_number = self.filter_list(response.css('.pdp-model_number::text').extract())
        item['ModelNumber'] = model_number[0] if model_number else 'N/A'

        item['SKU'] = response.css('.product_infotop::attr(data-sku)').get()

        images = response.css(".fancybox_img::attr(href)").extract()
        item['MainImage'] = images[0] if images else 'N/A'
        item['images'] = images
        if item['MainImage']:
            item.get('images').remove(item['MainImage'])

        item['AdditionalProperty'] = self.fetch_additional_property(
            response.css('#full-desc>div:nth-child(2) ::text').extract()[1:]
        )
        item['ProductDesc'] = " | ".join(response.css('#full-desc>div:nth-child(1) ::text').extract())

        model_name = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model name']
        model_name = model_name[0] if model_name else None
        item['ModelName'] = model_name

        if not item['ModelNumber']:
            model_number = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model number']
            model_number = model_number[0] if model_number else 'N/A'
            item['ModelNumber'] = model_number

        item['StockAvailability'] = self.get_stock_availability(response)
        item['Offer'] = clean_money_str('')
        item['RegularPrice'] = clean_money_str(response.css('.product_infotop .regular-price .price-num::text').get())

        if response.css('.product_infotop .old-price .price-num::text').get():
            item['RegularPrice'] = clean_money_str(response.css('.product_infotop .old-price .price-num::text').get())

        if response.css('.product_infotop .special-price .price-num::text').get():
            item['Offer'] = clean_money_str(response.css('.product_infotop .special-price .price-num::text').get())

        item['reviews'] = list()
        item['Rating'] = dict()
        # for i in enumerate(response.css('.prod_rvew_dl dd .rating::attr(style)').re('[\d]+')):
        #     item['Rating'][f"Rating{i + 1}"] = review
        raw_rating_value = response.xpath('//script/text()[contains(.,"ratingValue")]').re('ratingValue":"(.*?)"')
        item['RatingValue'] = float(raw_rating_value[0])/20 if raw_rating_value else 0
        raw_best_rating = response.xpath('//script/text()[contains(.,"bestRating")]').re('bestRating":(.*?),')
        item['BestRating'] = float(raw_best_rating[0])/20 if raw_best_rating else 0
        raw_reviews = response.xpath('//script/text()[contains(.,"ratingCount")]').re('ratingCount\s=\s"(.*?)"')
        item['ReviewCount'] = int(raw_reviews[0]) if raw_reviews else 0

        return item
