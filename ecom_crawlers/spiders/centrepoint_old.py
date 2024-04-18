import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemCentrePoint
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy




class CentrePointOldSpider(Spider):
    name = 'centrepoint_old'
    allowed_domains = ['www.centrepointstores.com', '3hwowx4270-dsn.algolia.net']
    main_url = 'https://www.centrepointstores.com/ae/en'
    products_api = 'https://3hwowx4270-dsn.algolia.net/1/indexes/*/queries?X-Algolia-API-Key=4c4f62629d66d4e9463ddb94b9217afb&X-Algolia-Application-Id=3HWOWX4270&X-Algolia-Agent=Algolia%20for%20vanilla%20JavaScript%20'
    headers = {'Content-Type': 'application/json'}
    body = {"requests":[{"indexName":"prod_uae_centrepoint_Product","params":"query=*&hitsPerPage=50&page={}&facets=*&facetFilters=%5B%5B%22inStockSSE%3A1%22%2C%22inStock%3A1%22%5D%2C%22approvalStatus%3A1%22%2C%5B%22allCategories%3Acp{}%22%5D%5D&getRankingInfo=1&clickAnalytics=true&attributesToHighlight=null&numericFilters=price%20%3E%200.9&query=*&attributesToRetrieve=concept%2CmanufacturerName%2Curl%2C333WX493H%2C345WX345H%2C550WX550H%2Cbadge%2Cname%2CwasPrice%2Cprice%2CemployeePrice%2CallCategories%2CshowMoreColor%2CproductType%2CchildDetail%2Csibiling%2CthumbnailImg%2CgallaryImages%2CisConceptDelivery%2CextProdType%2CreviewAvgRating%2CitemType%2CbaseProductId%2CflashSaleData%2CcategoryName&tagFilters=%5B%5B%22babyshop%22%2C%22splash%22%2C%22lifestyle%22%2C%22shoemart%22%2C%22centrepoint%22%2C%22shoexpress%22%2C%22sportsone%22%2C%22sminternational%22%2C%22lipsy%22%2C%22dawsonsports%22%2C%22mumsygift%22%2C%22morecare%22%2C%22ramrod%22%2C%22styli%22%2C%22trucare%22%2C%22trucaredropship%22%2C%22rivoli%22%2C%22timehouse%22%2C%22sambox%22%2C%22desertbeat%22%2C%22cpelite%22%2C%22mhsglobal%22%2C%22mapyr%22%2C%22grandstores%22%2C%22wonderbrand%22%2C%22drnutrition%22%2C%22jumboelectronics%22%2C%22desertbeatconloc%22%2C%22grandbaby%22%2C%22emsons%22%2C%22leafcompany%22%2C%22areeneast%22%2C%22elpan%22%2C%22supremeimpex%22%2C%22topgear%22%2C%22kermaventures%22%2C%22aliusie%22%2C%22triibedistribution%22%2C%22jossette%22%2C%22miniandyou%22%2C%22klugtoys%22%2C%22vdtrading%22%2C%22petsmartae%22%2C%22ichigoglobal%22%2C%22thinkplay%22%2C%22simbadickie%22%2C%22toytriangl%22%2C%22babico%22%2C%22playsmart%22%2C%22jayceebrands%22%2C%22brandhub%22%2C%22emaxdropship%22%2C%22jumbodropship%22%2C%22western%22%2C%22andadorbabywear%22%2C%22pinkandblue%22%2C%22mummazone%22%2C%22apparelgroup%22%2C%22montreal%22%2C%22wetrade%22%2C%22antworktrading%22%2C%22gigimedical%22%2C%22greenfuture%22%2C%22clovia%22%2C%22geopartnering%22%2C%22aalamialmutnawa%22%2C%22coega%22%2C%22justshop%22%2C%22shopfils%22%2C%22otantik%22%2C%22lscottonhome%22%2C%22msbm%22%2C%22biggbrands%22%2C%22wizzotoys%22%2C%22haidarous%22%2C%22oxiwave%22%2C%22liwa%22%2C%22zarabi%22%2C%22selfoss%22%2C%22ddaniela%22%2C%22bsapparelgroup%22%2C%22bsliwa%22%2C%22alfuttaim%22%2C%22shiphilinternational%22%5D%5D&analyticsTags=%5B%22en%22%2C%22Webmobile%22%5D&maxValuesPerFacet=*"}]}
    #Just make page and category name dynamic in body

    custom_settings = {
        'DOWNLOAD_DELAY': 0.75,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 300, 
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }
    page = 0
    count = 0
    
    categories = ['baby', 'women', 'kids', 'men', 'beauty', 'sports', 'homeandliving', 'electronics', 'pets']

    def start_requests(self):
        for category in self.categories:
            print("########################################", category)
            # Create a deep copy of the original body
            modified_body = copy.deepcopy(self.body)      
            # Modify the copy with the current category
            format_body = modified_body["requests"][0]["params"].format(self.page, category)
            modified_body["requests"][0]["params"] = format_body
            body = json.dumps(modified_body)
            yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, callback=self.parse, meta={'category':category, 'page':self.page})

    
    def parse(self, response):
        item = ProductItemCentrePoint()
        category = response.meta['category']
        print("Category: ", category)
        page = response.meta['page']
        data = json.loads(response.text)
        results = data.get('results', [])
        for result in results:
            hits = result.get('hits', [])
            if hits:
                self.count = 0
                for hit in hits:
                    item['name'] = hit.get('name', {}).get('en')
                    item['category'] = category
                    item['sub_categories'] = hit.get('allCategories', [])
                    item['rating'] = hit.get('reviewAvgRating', {}).get('avgProductRating', 0)
                    item['img'] = hit.get('gallaryImages', [])[0]
                    item['price_in_aed'] = hit.get('price')
                    item['old_price_in_aed'] = hit.get('wasPrice', 0)
                    url = next(iter(hit.get('url', {}).values()), "")
                    url = url.get('en', '')
                    item['url'] = self.main_url + url
                    item['object_id'] = hit.get('objectID')
                    item['page'] = page
                    
                    self.count+=1
                    yield item
                
                print("Category = {}, Total Products = {} on Page = {}".format(category, self.count, page))
                page = page + 1
                modified_body = copy.deepcopy(self.body)      
                format_body = modified_body["requests"][0]["params"].format(page, category)
                modified_body["requests"][0]["params"] = format_body
                body = json.dumps(modified_body)
                yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category':category, 'page': page})