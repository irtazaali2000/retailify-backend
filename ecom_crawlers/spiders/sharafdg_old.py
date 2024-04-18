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


class SharafDGOldSpider(Spider):
    name = 'sharafdg_old'
    ALGOLIA_KEYS = {
        'x-algolia-api-key': 'e81d5b30a712bb28f0f1d2a52fc92dd0',
        'x-algolia-application-id': '9KHJLG93J1',
        'x-algolia-agent': 'Algolia for vanilla JavaScript 3.24.9;JS Helper 2.23.2'
    }

    ALGOLIA_BASE = 'https://9khjlg93j1-2.algolianet.com/1/indexes'

    product_per_page = 24
    test_shelve_only = False
    test_urls = [
        # 'https://uae.sharafdg.com/c/computing/printers_ink/printers/',
        # 'https://uae.sharafdg.com/c/computing/printers_ink/inks_toners/',
        # 'https://uae.sharafdg.com/c/computing/printers_ink/',

        # "https://uae.sharafdg.com/?q=PlayStation%204%20Games&%20Dryers=&post_type=product"
        # 'https://uae.sharafdg.com/?q=Wearables&dFR[taxonomies.product_cat][0]=Smartwatches&post_type=product',
        # 'https://uae.sharafdg.com/?q=Networking%20%26%20Wireless&dFR[taxonomies.attr.Type][0]=Router&dFR[taxonomies.attr.Type][1]=WiFi%20Adapter&dFR[taxonomies.attr.Type][2]=Home%20Wi%20Fi%20System&dFR[taxonomies.attr.Type][3]=Whole%20Home%20Wi-Fi%20System&%20Storage=&post_type=product',
        # 'https://uae.sharafdg.com/?q=Camco&dFR[taxonomies.product_cat][0]=Cameras%20%26%20Camcorders&hFR[taxonomies.taxonomies_hierarchical][0]=Cameras%20%26%20Camcorders%20%3E%20Camcorders&post_type=product',
        # 'https://uae.sharafdg.com/?q=Receivers%20and%20Amplifiers&hFR[taxonomies.taxonomies_hierarchical][0]=TV%2C%20Video%20%26%20Audio&post_type=product',
        # 'https://uae.sharafdg.com/?q=Kitchen%20Appliances&hFR[taxonomies.taxonomies_hierarchical][0]=Home%20Appliances&%20Dryers=&post_type=product',
        # 'https://uae.sharafdg.com/?q=Men%20Watches&dFR[taxonomies.attr.Watches%20For][0]=Men&nR[price][%3C=][0]=1852&nR[price][%3E=][0]=37&post_type=product',
        # 'https://uae.sharafdg.com/?q=Women%20Watches&dFR[taxonomies.attr.Watches%20For][0]=Women&post_type=product',

        # 'https://uae.sharafdg.com/product/hp-officejet-pro-8023-all-in-one-printer1kr64b-2/',
        # 'https://uae.sharafdg.com/product/hp-officejet-pro-7740-wide-format-all-in-one-printer-g5j38a/',
        # 'https://uae.sharafdg.com/product/kingtex-bsf1130105-fitted-sheet/'
        # 'https://uae.sharafdg.com/product/apple-series-5-gps-cellular-44mm-gold-aluminium-case-with-pink-sand-sport-band/',
        # 'https://uae.sharafdg.com/product/lenovo-ideapad-l340-gaming-laptop-core-i7-2-6ghz-16gb-1tb256gb-4gb-win10-15-6inch-fhd-black/'
        # 'https://uae.sharafdg.com/product/sony-sel50f18f-fe-50mm-f1-8-lens/',
    ]
    rating_url_t = "https://d1le22hyhj2ui8.cloudfront.net/badge/sharafdg.com/reviews.json?key={}"
    description_url_t = "https://ws.cnetcontent.com/3f2c4539/script/45094ea3b2?cpn={sku}&mf={brand_name}&pn={model_no}"
    cat_name_t = "{prefix}.lvl{cat_lvl}:{cat_name}"
    hierarchical_cat_name_t = "{prefix}.product_cat.lvl{cat_lvl}:{cat_name}"
    custom_settings = {
        # "CONCURRENT_REQUESTS": 250,
        'DOWNLOAD_DELAY': 0.75,
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
        if self.test_shelve_only:
            for url in self.test_urls:
                yield Request(url, callback=self.parse_category)
                # yield Request(url)
            return

        for category in self.categories:
            for multi_cat in category['CategoryLink'].split(','):
                meta = {
                    'category': category,
                    'link': multi_cat,
                }
                yield Request(
                    url=multi_cat,
                    callback=self.parse_category,
                    meta=meta.copy()
                )

    def make_algolia_request(self, meta, page=0):
        post_url = "{}/*/queries?{}".format(
            self.ALGOLIA_BASE, urlencode(self.ALGOLIA_KEYS)
        )
        facet_filter = quote_plus(str(meta.get('facet_filter'))).replace('+', '%20')
        params = "query={query_param}&hitsPerPage={product_per_page}&maxValuesPerFacet=20&page={page}&attributesToRetrieve=permalink,permalink_ar,post_id,post_title,post_title_ar,discount,discount_val,images,price,sku,promotion_offer_json,regular_price,sale_price,in_stock,tags,rating_reviews,tags_ar&attributesToHighlight=post_title,post_title_ar&getRankingInfo=1&filters=post_status:publish AND price>0 AND in_stock:1 AND ee:1 AND archive:0&filters=post_status%3Apublish&facets=%5B%22tags.title%22%2C%22taxonomies.attr.Brand%22%2C%22price%22%2C%22taxonomies.attr.Processor%22%2C%22taxonomies.attr.Screen%20Size%22%2C%22taxonomies.attr.Internal%20Memory%22%2C%22taxonomies.attr.Storage%20Size%22%2C%22taxonomies.attr.RAM%22%2C%22taxonomies.attr.Graphics%20Card%22%2C%22taxonomies.attr.Color%22%2C%22taxonomies.attr.OS%22%2C%22taxonomies.attr.Megapixel%22%2C%22taxonomies.attr.Capacity%22%2C%22taxonomies.attr.Loading%20Type%22%2C%22taxonomies.attr.Tonnage%22%2C%22taxonomies.attr.Compressor%20Type%22%2C%22taxonomies.attr.Star%20Rating%22%2C%22taxonomies.attr.Energy%20input%22%2C%22taxonomies.attr.Water%20Consumption%22%2C%22taxonomies.attr.Control%20Type%22%2C%22taxonomies.attr.Number%20of%20Channels%22%2C%22taxonomies.attr.Audio%20Output%22%2C%22taxonomies.attr.No%20of%20Burners%2FHobs%22%2C%22taxonomies.attr.Type%22%2C%22taxonomies.attr.HDMI%22%2C%22taxonomies.taxonomies_hierarchical.product_cat.lvl0%22%2C%22taxonomies.taxonomies_hierarchical.product_cat.lvl1%22%5D&tagFilters=&facetFilters={facet_filter}"  # NOQA
        data = {
            "requests": [
                {
                    "indexName": "products_index",
                    "params": params.format(
                        query_param=meta.get('query_param'),
                        page=page,
                        facet_filter=facet_filter,
                        product_per_page=self.product_per_page
                    )
                }
            ]
        }
        yield Request(
            url=post_url, callback=self.parse_product_links, dont_filter=True,
            body=json.dumps(data), meta=meta.copy(), method='POST',
            # Required referer, otherwise it's got 403
            headers={'Referer': meta.get('friendly_url')}
        )

    def parse_category(self, response):
        meta = response.meta.copy()
        cat_name = response.xpath(
            '//script/text()[contains(.,"catName=")]'
        ).re(r'="(taxonomi.*?)";')
        query_param = ''
        if not cat_name:
            if "q=" in response.url:
                query_param = re.findall("q=(.*?)&", response.url)[0]
                self.logger.info('Query Param Found %s', query_param)

            raw_cat = re.findall("FR(.*?)&", response.url)
            if raw_cat:
                raw_unquote = unquote(raw_cat[0])
                get_cat = re.findall("=(.*)", raw_unquote)[0]
                cat_lvl = re.findall("([\d])]", raw_unquote)[0]
                cat_prefix = re.findall("\[(.*?)]", raw_unquote)[0]
                if cat_lvl == '0':
                    if "taxonomies_hierarchical" in cat_prefix:
                        cat_name = self.hierarchical_cat_name_t.format(prefix=cat_prefix, cat_lvl=cat_lvl,
                                                                       cat_name=get_cat)
                    else:
                        cat_name = self.cat_name_t.format(prefix=cat_prefix, cat_lvl=cat_lvl, cat_name=get_cat)
                        cat_name = [cat_name.replace('.lvl0', '')]
                else:
                    cat_name = [self.cat_name_t.format(prefix=cat_prefix, cat_lvl=cat_lvl, cat_name=get_cat)]

                self.logger.warning('Category Found from URL: %s', response.url)
            else:
                self.logger.warning('No FR category name found %s', response.url)

        friendly_category = ''
        if not (query_param and not raw_cat):
            facet_string = '[["%s"]]'
            cat_name = cat_name[0].replace('&amp;', '&') if cat_name else ''
            friendly_category = cat_name.split(':')[-1] if cat_name else ''
            friendly_category_count = len(friendly_category.split(">"))
            try:
                cat_level = friendly_category_count
                if cat_level > 1:
                    cat_level -= 1
                else:
                    cat_level = 1
                cat_name = re.sub(r'lvl\d', 'lvl%s' % cat_level, cat_name)
            except IndexError:
                cat_name = re.sub(r'lvl\d', 'lvl1', cat_name)

            cat_name = facet_string % cat_name

        meta['query_param'] = query_param
        meta['facet_filter'] = cat_name
        meta['friendly_category'] = friendly_category
        meta['friendly_url'] = response.url
        for req in self.make_algolia_request(meta=meta):
            yield req

    def parse_product_links(self, response):
        json_data = json.loads(response.text).get('results')[0]
        current_page = response.meta.get('page_number', 1)
        total_page = json_data.get('nbPages')
        category = response.meta.get('friendly_category')
        friendly_url = response.meta.get('friendly_url')
        print(f"{current_page}-{total_page}-{friendly_url}")
        # if total_page == 0:
            # if friendly_url not in self.test_urls:
            # a = "b"
        for product in json_data.get('hits'):
            meta = response.meta.copy()
            yield Request(product['permalink'], meta=meta.copy(), callback=self.parse_product)

        if current_page < total_page:
            meta = response.meta.copy()
            meta.update({'page_number': current_page + 1})
            for req in self.make_algolia_request(meta, page=current_page):
                yield req

    def fetch_model_and_sku(self, ms_selector):
        raw = {}
        for sel in ms_selector:
            if "model" in sel.css("::text").get().lower():
                raw['model'] = sel.css("span::text").get()
            if "sku" in sel.css("::text").get().lower():
                raw['sku'] = sel.css("span::text").get()
        return raw

    def fetch_additional_property(self, sels):
        raw_additional_pr = []
        if sels:
            for sub_sels in sels:
                for sub_sel in sub_sels.css("tr"):
                    if sub_sel.css("td").get():
                        raw_additional_pr.append({
                            'name': sub_sel.css(".specs-heading::Text").get().strip(),
                            'value': sub_sel.css('td::text').extract()[-1].strip()
                        })
        return raw_additional_pr

    def get_stock_availability(self, response):
        raw_stock_check = response.css(".pdp-price-cart").re("isproductInStock\s=\s\'(.*)\';")
        return True if raw_stock_check else False

    def parse_product(self, response):
        # def parse(self, response):

        item = dict()
        item['VendorCode'] = self.vendor_code
        category = response.meta.get('category')
        item['CatalogueCode'] = category['CatalogueCode']
        item['CategoryCode'] = category['CategoryCode']
        raw_breadcrumbs = response.css('.breadcrumb li span::text').extract()
        item['CatalogueName'] = raw_breadcrumbs[1]
        item['CategoryName'] = raw_breadcrumbs[-2]

        item['ProductName'] = response.css(".product_title ::text").get()
        raw_model_sku = self.fetch_model_and_sku(response.css(".prod-extra .reset-margin"))
        item['SKU'] = raw_model_sku['sku']
        item['ModelNumber'] = raw_model_sku['model']
        images = response.css('.mainproduct-slider img::attr(src)').extract()
        item['MainImage'] = images[0] if images else 'N/A'
        item['images'] = images
        item.get('images').remove(item['MainImage'])
        item['URL'] = response.url
        raw_brand = response.xpath('//td[@itemprop="brand"]//text()').get()
        item['BrandName'] = raw_brand.strip() if raw_brand else 'N/A'

        item['AdditionalProperty'] = self.fetch_additional_property(response.css('.product-spec'))

        model_name = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model name']
        model_name = model_name[0] if model_name else None
        item['ModelName'] = model_name

        if not item['ModelNumber']:
            model_number = [mn['value'] for mn in item['AdditionalProperty'] if mn['name'].lower() == 'model number']
            model_number = model_number[0] if model_number else None
            item['ModelNumber'] = model_number

        item['StockAvailability'] = self.get_stock_availability(response)

        item['RegularPrice'] = clean_money_str(
            response.css(".pdp-price-cart .total--sale-price::attr(data-sale-price)").get())
        item['Offer'] = clean_money_str('')

        if response.css('.pdp-price-cart .cross-price .strike::text').get():
            item['Offer'] = item['RegularPrice']
            item['RegularPrice'] = clean_money_str(response.css('.pdp-price-cart .cross-price .strike::text').get())

        canonical_sku = response.xpath("//meta[@property='product:retailer_part_no']/@content").get() or item[
            'SKU'].zfill(18)

        item['ProductDesc'] = " | ".join(self.fetch_description(
            response.css('.specs-wrp.d div ::Text').extract() or response.css('#ccs-inline-content ::Text').extract()))
        if item['ProductDesc']:
            return Request(
                self.rating_url_t.format(canonical_sku),
                self.parse_rating,
                meta={'item': item.copy(),
                      "canonical_sku": canonical_sku}
            )

        return Request(
            self.description_url_t.format(sku=canonical_sku,
                                          brand_name=item['BrandName'],
                                          model_no=item['ModelNumber']),
            self.parse_description,
            meta={'item': item.copy(),
                  "canonical_sku": canonical_sku}
        )

    def clean_script_tags(self, val):
        return re.sub("(<script .* ?<\/script>)", "", val) if val else ''

    def fetch_description(self, descriptions):
        raw_description = []
        for index, description in enumerate(descriptions):
            if "ccs_cc_args" in description:
                continue
            raw_description.append(description.strip() if description else '')
        return list(filter(None, raw_description))

    def parse_description(self, response):
        item = response.meta.get('item')
        canonical_sku = response.meta.get('canonical_sku')
        description = re.findall('html\":\s\"(.*)" }', response.text)
        desc_resp = HtmlResponse(
            url="my HTML string",
            body=description[0].replace("\\n", "").replace("\\", ""),
            encoding='utf-8') if description else ''

        item['ProductDesc'] = " | ".join(desc_resp.css("div ::Text").extract())
        if item['ProductDesc']:
            self.logger.info("Product description collected from description api!")
        else:
            self.logger.info("No Description Found!")
        return Request(
            self.rating_url_t.format(canonical_sku),
            self.parse_rating,
            meta={'item': item.copy(),
                  "canonical_sku": canonical_sku}
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

        reviews = [x + y for x, y in zip(raw_reviews.get('pro_score_dist_all'), raw_reviews.get('user_score_dist_all'))]
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

        if not self.reviews:
            return item

        user_review_url = raw_reviews.get('user_review_url')
        pro_review_url = raw_reviews.get('pro_review_url')
        if user_review_url:
            return Request(
                url=user_review_url,
                callback=self.parse_reviews,
                meta={
                    'item': item,
                    'pro_review_url': pro_review_url,
                }
            )
        elif pro_review_url:
            return Request(
                url=pro_review_url,
                callback=self.parse_reviews,
                meta={
                    'item': item,
                }
            )
        else:
            return item

    def parse_reviews(self, response):
        item = response.meta['item']
        pro_review_url = response.meta.get('pro_review_url')
        reviews = response.meta.get('reviews', list())
        raw_reviews = json.loads(response.text)
        reviews.extend(
            [
                {
                    'CommentDate': review.get('date'),
                    'Source': review.get('source'),
                    'Comment': review.get('extract')
                }
                for review in raw_reviews.get('reviews')
            ]
        )

        next_page = raw_reviews.get('next_page_url')
        if next_page:
            return Request(
                next_page,
                self.parse_reviews,
                meta={
                    'item': item,
                    'reviews': reviews,
                    'pro_review_url': pro_review_url
                }
            )

        if pro_review_url:
            return Request(
                pro_review_url,
                self.parse_reviews,
                meta={
                    'item': item,
                    'reviews': reviews,
                }
            )

        item['reviews'] = reviews
        return item
