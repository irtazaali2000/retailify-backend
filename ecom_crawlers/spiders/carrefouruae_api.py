import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItem
from ecom_crawlers.utils import *
from fake_useragent import UserAgent

ua = UserAgent()

def clean(str_or_lst):
    if str_or_lst is None:
        return
    if not isinstance(str_or_lst, str) and getattr(str_or_lst, '__iter__', False):
        return [j for j in (_clean_val(i) for i in str_or_lst if i is not None) if j]
    return _clean_val(str_or_lst)


def _clean_val(val):
    return re.sub('\s+', ' ', val.replace('\xa0', ' ')).strip()


class CarrefourUaeSpider(Spider):
    name = 'carrefour_api'
    # product_url = 'https://www.carrefouruae.com/p/{}'
    #cat_url = 'https://www.carrefouruae.com/api/v1/countries/uae/zones/D05/search/categories/{}?sortBy=relevance&currentPage=0&pageSize=60&lang=en'
    #search_url = 'https://www.carrefouruae.com/api/v1/countries/uae/zones/D05/search?keyword={}&sortBy=relevance&currentPage=0&pageSize=60&lang=en'
    start_urls = ['https://www.carrefouruae.com']
    
    main = 'https://www.carrefouruae.com'

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': '*/*',
        'User-Agent': ua.random,
        'Appid': 'Reactweb',
       # 'Cookie': 'maf-session-id=FBD8D8E8-89D4-D9B5-5993-DFA5E6B426FA; storeInfo=mafuae|en|AED; mafuae-preferred-delivery-area=DubaiFestivalCity-Dubai; prevAreaCode=DubaiFestivalCity-Dubai; cart_api=v2; AKA_A2=A; bm_sz=61B05DD7D71AC725497E644D15AC0678~YAAQQ9s4fRVOsqqNAQAAUGG5yxa6/Ha6goe2wIS6NhcReSYfiThFDejpqvEJV253ixHcTPk56rszh1gDw9+fL3U034s4ZswZfsSp/yiWbAAU2Gqm9+MD25w3fO+DqUPCjgz/ZHbI4/gi1CeyxguGzoENsm8cFc/8z1uf8zzqlSjb6YBlTqNuLuG0P/zinTbISnqmc+dBB0pk7T8xYcf8jfowqviQbXMh1aAT8hQK6T5ZY7tIUDIpXgXxqu5bEIaXApFC4EWu/bSxi3wBw4uryMtEwado4ldnc/tDk3JTxZDdPzEnCeMKHRLvcS91zELYCbnsIdKOu6FiHRH1a8ahtZXKrQgjP+bqEH7TVxaoOcAZhZDSYg0Jeq7NLln5MQ==~3224377~4535607; _gcl_au=1.1.1678678595.1708519944; _gid=GA1.2.1621432106.1708519944; _scid=23903945-15a9-4338-8b81-e84cab5bf452; _fbp=fb.1.1708519945251.302931805; _sctr=1%7C1708473600000; _abck=809CE05C34D0139BA9E1AECC0371E56A~0~YAAQQ9s4ff5QsqqNAQAAboG5ywsscrUL6t9aUozGXsS3aY5fuvSpejZefagRgnz2wHZ35vPWDBt2l/Wt6VaFEEbC7LdhNdZEuOEmGUtuuDcKYxTI8+wMAw+veIo0mvKXdHI24aZpi7I5BEgojxHjEbJCT/bg3W4QlyGuU5z5xOzUpLRdUZEidfjzkPIgG6fBkIg5VeaShiQxXIASX37kieW5v7/Zg/NL5raT5+bzHx7VFWzYzoccBany3M5rxpLkB2//hho06TEKhJ0X15TiEMj/FvxHKgvtRk9OdFC5mtjxFxQZrZ5h11dTKjXeZ4OlpNwDc11ipTfnG7BWxhPIU3KbKLJNtg+9mpe0SXGtzFHr6FhNfknD9nJCzb3aSR9IKLTeJXy9IDkPQGi8qyMgoAp6oiDNbjOJcBlItiZj~-1~-1~-1; hideCoachMark=true; OptanonAlertBoxClosed=2024-02-21T12:52:55.568Z; app_version=v4; search_type=search_native; JSESSIONID=F0993BC06A899DB501A0538E4A71C349.accstorefront-79ff97967d-5b27q; mafuae-web-preferred-delivery-area="Dubai Festival City - Dubai"; ROUTE=.accstorefront-79ff97967d-5b27q; isNowJourney=true; page_type=home; __gads=ID=f5abe3cd74db843c:T=1708519963:RT=1708520855:S=ALNI_MbeyBcvWy69rt7QEg3rIyfEN9EEoQ; __gpi=UID=00000d2b89b1ed7b:T=1708519963:RT=1708520855:S=ALNI_MbOVuRV7NocaXwUFLYXkEt-XpFDuA; __eoi=ID=67c08968aa9329bd:T=1708519963:RT=1708520855:S=AA-AfjYOOgdY4tRX05UCeoAbZzhk; _scid_r=23903945-15a9-4338-8b81-e84cab5bf452; TEAL=v:618dcbb9711756039851612194743556f3027677856$t:1708522672347$s:1708519944478%3Bexp-sess$sn:1$en:16; _ga=GA1.2.237139437.1708519944; cto_bundle=NN4CCl8xRHl1eSUyRm1WZnlrM3lqcUlBMUdTZ0F3RG9UQkpzZDFKbjgxa3JTdWVpMjFKR0FwR2Z3c0dUV2FWTFd5UkxXb1hRcFV2WndqUnlqVG9FaGZSUjZvdmV2RG1JV1BBYWZGeDNKTXFUNEJHRm1iNlVOWGRKZ3d1Vmx4MCUyRlhnQk03JTJCWTVacVFFbUZCYTg5U3hmZ1YlMkZiTkM3TTElMkZPc2s2NkdaRThJZmhvME5XY3JrJTNE; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Feb+21+2024+13%3A07%3A54+GMT%2B0000+(Greenwich+Mean+Time)&version=202301.2.0&isIABGlobal=false&hosts=&consentId=9915350a-b0ba-43ed-8746-5772a54f8b16&interactionCount=1&landingPath=NotLandingPage&groups=C0004%3A1%2CC0001%3A1%2CC0002%3A1%2CC0003%3A1&geolocation=PK%3BSD&AwaitingReconsent=false; _ga_BWW6C6N1ZH=GS1.1.1708519944.1.1.1708521301.60.0.0; RT="z=1&dm=www.carrefouruae.com&si=576c1839-6e63-47b4-9993-786cb91986db&ss=lsvsnpjy&sl=f&tt=u3e&obo=a&rl=1"',
        'Referer': 'https://www.carrefouruae.com/mafuae/en/',
        'Storeid': 'mafuae',
        'Token': '',
        'Traceparent': '',
        'Tracestate': '',
        'Newrelic': '',
        'Env': 'prod',
        'Lang': 'en',
        'Langcode': 'en',
        'Userid': 'anonymous'
    }
    #products_api = """https://www.carrefouruae.com/api/v2/products?ids=[{}]&lang=en&areaCode=Ibn%20Battuta%20Mall%20-%20Dubai"""
    # product_api = """https://www.carrefouruae.com/v3/products/mafuae/en/productService/v2/pdp/{}?areacode=Dubai%20Festival%20City%20-%20Dubai&fields=FULL&app_id=Reactweb&displayCurr=AED"""
    
    cat_url = 'https://www.carrefouruae.com/api/v1/menu?latitude=25.2171003&longitude=55.3613635&lang=en&displayCurr=AED'
    products_api = 'https://www.carrefouruae.com/v1/relevance/mafuae/en/keyword?keyword=*&lang=en&placements=home_page.web_rank17|home_page.web_rank2|home_page.web_rank9|home_page.placement13&latitude=25.2171003&longitude=55.3613635'
    
    products_api_2 = 'https://www.carrefouruae.com/api/v4/relevance/products/F1600000?lang=en&placements=category_page.clp_web_rank3|category_page.clp_web_rank6|category_page.clp_web_rank1|category_page.clp_web_rank2|category_page.clp_web_rank4&displayCurr=AED&latitude=25.2171003&longitude=55.3613635'
    products_api_3 = 'https://www.carrefouruae.com/api/v4/relevance/products/F1700000?lang=en&placements=category_page.clp_web_rank3|category_page.clp_web_rank6|category_page.clp_web_rank1|category_page.clp_web_rank2|category_page.clp_web_rank4&displayCurr=AED&latitude=25.2171003&longitude=55.3613635'
    search_url = 'https://www.carrefouruae.com/v1/relevance/mafuae/en/keyword?keyword=*&lang=en&placements=home_page.web_rank17|home_page.web_rank2|home_page.web_rank9|home_page.placement13&latitude=25.2171003&longitude=55.3613635'
    count = 0
    total_products = []
    test_shelve_only = False
    test_urls = [
        'https://www.carrefouruae.com/mafuae/en/baby-formula-0-6-months-/aptamil-advance-1-900-g/p/1783640?list_name=carousel%7Cmilk%2C_food_%26_juices%7Cmilk%2C_food_%26_juices&offer=offer_carrefour_'
    ]
    #categories = [{'CategoryLink': 'https://www.carrefouruae.com/mafuae/en/smartphones-tablets-wearables/smartphones-wearables/mobile-phones/c/NF1220100'}]
    #ids = []
    seen_ids = []
    # logging.getLogger().addHandler(logging.StreamHandler())
    #recommended_products = []

    custom_settings = {
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY':2,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 15,  # Set a reasonable timeout in seconds

      #  'URLLENGTH_LIMIT': 8000,
        #'LOG_STDOUT': False,
        #'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',

    }

    def __init__(self, reviews='False', short_scraper="False", *args, **kwargs):
        self.reviews = reviews.lower() == 'true'
        self.short_scraper = short_scraper.lower() == 'true'
        catalogue_url = CATALOGUE_URL_T.format(self.name, self.short_scraper)
        categories_url = "{}{}".format(HOST, catalogue_url)
        raw_res = requests.get(categories_url).json()
        self.categories = raw_res.get('data', [])
        self.vendor_code = raw_res.get('VendorCode')
        # print(raw_res)

        
    def start_requests(self):

        print("Start Requests called!")

        if self.test_shelve_only:
            for url in self.test_urls:
                yield Request(url,
                              callback=self.parse_product_links,
                              # errback=self.parse_error
                              )
            print("return...")
            return
        print("1")
        for category in self.categories:

            for multi_cat in category['CategoryLink'].split(','):

                meta = {
                    'category': category,
                    'link': multi_cat,
                    'page': 1
                }

                print(f"Requesting search API for category: {multi_cat}")

                # yield Request(
                #     url=self.search_url,
                #     callback=self.parse_product_links,
                #     headers=self.headers,
                #     method='GET',
                #     meta=meta.copy()
                # )

                yield Request(self.products_api, callback=self.parse_product_links, method = 'GET', meta=meta.copy(), headers=self.headers)
                yield Request(self.products_api_2, callback=self.parse_product_links, method = 'GET', meta=meta.copy(), headers=self.headers)
                yield Request(self.products_api_3, callback=self.parse_product_links, method = 'GET', meta=meta.copy(), headers=self.headers)


    def parse_product_links(self, response):
        meta = response.meta.copy()
        raw_products = json.loads(response.text)
        total_pages = raw_products.get('nbPages', 1)
        current_page = meta['page']

        placement = raw_products.get('placements', [])
        for place in placement:
            recommended_products = place.get('recommendedProducts', [])
            for product in recommended_products:
                item = ProductItem(
                    ProductId=product.get('id'),
                    ProductName=product.get('name'),
                    RegularPrice=product.get('price', {}).get('price'),
                    CategoryName=product.get('category', [])[0].get('name', ''),
                    StockAvailability=product.get('availability', {}).get('isAvailable'),
                    BrandName=product.get('brand', {}).get('name', ''),
                    URL=self.main + (product.get('links', {}).get('productUrl', {}).get('href', '')),
                    MainImage=product.get('links', {}).get('images', [])[0].get('href', '')
                )
                
                yield item
                
                self.logger.info(f"Extracted item: {item}")
        print("No more pages to request.")


