import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ecom_crawlers.utils import *


def clean(str_or_lst):
    if str_or_lst is None:
        return
    if not isinstance(str_or_lst, str) and getattr(str_or_lst, '__iter__', False):
        return [j for j in (_clean_val(i) for i in str_or_lst if i is not None) if j]
    return _clean_val(str_or_lst)


def _clean_val(val):
    return re.sub('\s+', ' ', val.replace('\xa0', ' ')).strip()


class CarrefourUaeSpider(Spider):
    name = 'carrefourold'
    # product_url = 'https://www.carrefouruae.com/p/{}'
    #cat_url = 'https://www.carrefouruae.com/api/v1/countries/uae/zones/D05/search/categories/{}?sortBy=relevance&currentPage=0&pageSize=60&lang=en'
    #search_url = 'https://www.carrefouruae.com/api/v1/countries/uae/zones/D05/search?keyword={}&sortBy=relevance&currentPage=0&pageSize=60&lang=en'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
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
    search_url = 'https://www.carrefouruae.com/v1/relevance/mafuae/en/keyword?keyword=*&lang=en&placements=home_page.web_rank17|home_page.web_rank2|home_page.web_rank9|home_page.placement13&latitude=25.2171003&longitude=55.3613635'

    test_shelve_only = False

    #categories = [{'CategoryLink': 'https://www.carrefouruae.com/mafuae/en/smartphones-tablets-wearables/smartphones-wearables/mobile-phones/c/NF1220100'}]
    seen_ids = []
    # logging.getLogger().addHandler(logging.StreamHandler())


    custom_settings = {
        'DOWNLOAD_DELAY':1.5,
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
        print("Inside start_requests")
        for category in self.categories:
            for multi_cat in category['CategoryLink'].split(','):
                meta = {
                    'category': category,
                    'link': multi_cat,
                }

                #print("Category: ", category)
                #print("Link: ", multi_cat)
                if 'search' in multi_cat:
                    print("Hello")
                    keyword = re.findall('search=(.*)\??', multi_cat)[0].split('?')[0]
                    multi_cat = self.search_url#.format(keyword)
                elif '/c/' in multi_cat:
                    print("Hi")
                    category = multi_cat.split('/c/')[1].split('?')[0]
                    multi_cat = self.cat_url#.format(category)
                yield Request(
                    #url=multi_cat,
                    url=self.products_api,
                    callback=self.parse_home,
                    meta=meta.copy(),
                    headers=self.headers
                )

    def parse_home(self, response):
        print("Inside parse_home")

        #yield from self.parse_products_link(response)

        data = json.loads(response.text)
        #print("Data in parse_home: ", data)
        total_pages = data['numOfPages']
        print(total_pages)
        for i in range(1, total_pages):
            url = response.url.replace('currentPage=0', f'currentPage={i}')
            meta = response.meta.copy()
            headers = {
                'referer': response.url
            }
            print(f"{i} - {total_pages} - {url}")
            yield Request(url, callback=self.parse_products_link, meta=meta, headers=self.headers)

    def parse_products_link(self, response):
        print("Inside parse_products_link")

        data = json.loads(response.text)
        #print("Data in parse_products_links: ", data)
        print("Yahannnnn")
        print("Yeh raha: ", data['placements'][0]['recommendedProducts'][0]['name'])
        ids = [link['productId'] for link in data['products'] if link['productId'] not in self.seen_ids]
        print(ids)
        self.seen_ids.extend(ids)
        headers = self.headers.copy()
        headers['appid'] = 'Reactweb'
        for id in ids:
            url = self.products_api#.format(id)
            yield Request(url, meta=response.meta.copy(), headers=self.headers, callback=self.parse_product)

    def parse(self, response):
        print("Inside parse")
        for request in super(CarrefourUaeSpider, self).parse(response):
            if isinstance(request, Request):
                merged_meta = {**response.meta, **request.meta}
                request = request.replace(meta=merged_meta.copy())

                yield request

    def parse_product(self, response):
        print("Inside parse_product")

        raw_product = json.loads(response.text)
        item = dict()
        category = response.meta.get('category')

        if not (self.test_shelve_only):
            item['VendorCode'] = self.vendor_code
            item['CatalogueCode'] = category['CatalogueCode']
            item['CategoryCode'] = category['CategoryCode']

        item['SKU'] = raw_product['code']
        item["ProductName"] = raw_product['name'].replace('&quot;', '"').replace('&amp;', '&')
        item['URL'] = response.urljoin(raw_product['url'])
        item["BrandName"] = raw_product["brandName"]
        item["StockAvailability"] = raw_product['stock']['isAvailable'] if 'stock' in raw_product else True
        if not item["StockAvailability"]:
            item["StockAvailability"] = raw_product['isBuyNowProduct'] if 'isBuyNowProduct' in raw_product else True
        item['ProductDesc'] = self.product_desc(raw_product)
        item['AdditionalProperty'] = self.additional_property(raw_product)

        self.parse_images(item, raw_product)
        self.parse_prices(item, raw_product)
        self.parse_ratings(item, raw_product)
        self.parse_category(item, raw_product)
        yield item

    def parse_images(self, item, raw_product):
        print("Inside parse_images")

        images = [i['url'] for i in raw_product['images'] if i['format'] == 'productZoom']
        item['MainImage'] = images[0] if images else ''
        item['images'] = images[1:] if images and len(images) > 1 else []

    def parse_prices(self, item, raw_product):
        print("Inside parse_prices")

        if 'mainOffer' in raw_product:
            price = raw_product['mainOffer']
            item['RegularPrice'] = clean_money_str(str(price['price']['price']))
            item['Offer'] = clean_money_str(str(price['price']['discount']['price'])) \
                if 'discount' in price['price'] else format(0.0, '.2f')
        else:
            item['RegularPrice'] = raw_product['price']['price']
            item['Offer'] = format(0.0, '.2f')

    def additional_property(self, raw_product):
        print("Inside additional_property")

        if 'classifications' in raw_product:
            return {j['name']: ', '.join([k['value'] for k in j['featureValues']])
                    for i in raw_product['classifications'] for j in i['features']}
        return []

    def product_desc(self, raw_product):
        print("Inside parse_desc")
        
        text = raw_product.get('description', '') + raw_product.get('marketingText', '')
        return ' | '.join(clean(Selector(text=text).css('::text').getall()))

    def parse_ratings(self, item, raw_product):
        print("Inside parse_ratings")

        if 'averageRating' in raw_product and 'reviews' in raw_product:
            ratings = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
            for i in raw_product['reviews']:
                ratings[i['rating']] += 1
            item['BestRating'] = max([i for i in ratings if ratings[i]])
            item['ReviewCount'] = raw_product['numberOfReviews']
            item['RatingValue'] = raw_product['averageRating']
            item['Rating'] = {f"Rating{i}": ratings[i] for i in ratings}
        else:
            item['Rating'] = dict()
            item['RatingValue'] = 0
            item['BestRating'] = 0
            item['ReviewCount'] = 0

    def parse_category(self, item, raw_product):
        print("Inside parse_category")

        raw_cats = [i['name'] for i in raw_product['categoriesHierarchy']]
        if raw_cats:
            item['CatalogueName'] = raw_cats[0]
            item['CategoryName'] = raw_cats[-1]
