from datetime import datetime

import requests
from ecom_crawlers.settings import HOST, PRODUCTS_URL_T
from scrapy import Spider, Request
from ecom_crawlers.utils import *


class StockUpdate(Spider):

    name = 'stock-update'
    headers = {
        'content-type': 'application/json',
    }
    custom_settings = {
        'DOWNLOAD_DELAY': 0.90,
        'RETRY_TIMES': 15,
        'URLLENGTH_LIMIT': 8000,
        'LOG_STDOUT': False,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
    }

    def __init__(self, spider_name="noon", *args, **kwargs):

        #For updating the stock Availability
        self.api = '{}/api/v1/private/product/update_stock_availability/'.format(HOST)

        product_url = PRODUCTS_URL_T.format(spider_name)
        product_url = "{}{}".format(HOST, product_url)
        self.product_urls = requests.get(product_url).json()
        self.headers = {
            'content-type': 'application/json',
        }

    def start_requests(self):
        for url in self.product_urls.get('product_details'):
            yield Request(
                url=url['URL'],
                callback=self.parse,
                errback=self.parse_error,
            )

    def send_update(self, data):
        res = requests.post(
            self.api,
            json=data
        )
        res.raise_for_status()
        return

    def parse_error(self, failure):
        if failure.value.response.status == 404:
            data = {
                'StockAvailability': False,
                'URL': failure.value.response.url,
            }
            print(f"{failure.value.response.status}: {data['StockAvailability']}")
            self.send_update(data)

    def parse(self, response):
        StockAvailability = get_noon_stock_availability(response)
        print(StockAvailability)
        data = {
            'StockAvailability': StockAvailability,
            'URL': response.url,
        }
        self.send_update(data)

