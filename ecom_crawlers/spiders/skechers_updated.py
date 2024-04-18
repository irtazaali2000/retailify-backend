import re
import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemSkechers
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
from fake_useragent import UserAgent




class SkechersWEBSpider(Spider):
    name = 'skechersWEB'
    allowed_domains = ['skechers.com', 'edge.curalate.com']
    main_url = 'https://www.skechers.com'


    
    cat_urls = {
        'Men': 'https://www.skechers.com/men/shoes/',
        'Women': 'https://www.skechers.com/women/',
        'Kids': 'https://www.skechers.com/kids/',
        'Clothing': 'https://www.skechers.com/clothing-accessories/',
        'Comfort Technologies':'https://www.skechers.com/technologies/comfort-technologies/',
        'Features': 'https://www.skechers.com/technologies/features/',
    }

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 200,
        #'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    page = 0
    count = 0
    

    
    def start_requests(self):
        ua = UserAgent()
        headers = {
            'authority': 'www.skechers.com',
            'method': 'GET',
            #'path': '/men/shoes/',
            'scheme': 'https',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            #'Cookie': '_pin_unauth=dWlkPU1XSmtOak0wTnprdE1USXdZUzAwTWpjM0xUbG1OVGt0TnpobE56WTRNV1U0T0dFeg; _pin_unauth=dWlkPU1XSmtOak0wTnprdE1USXdZUzAwTWpjM0xUbG1OVGt0TnpobE56WTRNV1U0T0dFeg; dwanonymous_63ec983096393364be678ab69485089e=abuBK2q9xOjPkqhAT2x8TYoJZS; _gcl_au=1.1.368407137.1710483727; mt.v=2.1867057858.1710483729522; _pxvid=57241ce2-e294-11ee-b406-7c7636302117; __cq_uuid=abuBK2q9xOjPkqhAT2x8TYoJZS; ajs_anonymous_id=d54fee02-259f-42b7-9818-224b52f230d8; _px_f394gi7Fvmc43dfg_user_id=NWMwZGNlYjAtZTI5NC0xMWVlLWFlZjQtNmJiNWI5MDkzODk1; __attentive_id=e9295cc565274b97b091c42fffd7e3a6; _attn_=eyJ1Ijoie1wiY29cIjoxNzEwNDgzNzMzNDM1LFwidW9cIjoxNzEwNDgzNzMzNDM1LFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcImU5Mjk1Y2M1NjUyNzRiOTdiMDkxYzQyZmZmZDdlM2E2XCJ9In0=; __attentive_cco=1710483733443; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%228vLe62iWbfJFlkwwJSzt%22%7D; _tt_enable_cookie=1; _ttp=bYOr5APe7kKmLwW0Pa0R8-So-y_; __ruid=45123878-s1-k4-42-1p-995o6bplm96ze14h9iox-1710483734576; __rcmp=0!bj1fZ2MsZj1nYyxzPTEsYz05NzA1LHRyPTEwMCxybj01MDksdHM9MjAyNDAzMTUuMDYyMixkPXBjO249cncxLGY9cncscz0xLGM9MjYxOSx0PTIwMjAwNzIxLjEyNTg~; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22unknown%22%7D; _scid=c6239578-af94-4e9b-8bcc-c336872e4ed8; _fbp=fb.1.1710483737194.262155026; ndp_session_id=359c9a0c-8812-4cfb-9368-6939d70ba7ea; QuantumMetricUserID=443a8dcc45ad1842e6255c209930b4c7; crl8.fpcuid=ca6cabe0-45ec-491c-af14-58753e53c59e; __pr.7x0=bhpLATWu85; dwac_3a60353a3ab037178b206f9956=60HpL-jGedQ375GLGiyCrBCvNyg93BPVOnY%3D|dw-only|||USD|false|America%2FLos%5FAngeles|true; cqcid=abuBK2q9xOjPkqhAT2x8TYoJZS; cquid=||; sid=60HpL-jGedQ375GLGiyCrBCvNyg93BPVOnY; __cq_dnt=0; dw_dnt=0; dwsid=VYoior7pCLJxuAN6VnlJda5k_KVr82KzfCGEC_o2wFEM_J5MLzV8N-XAHNQ1xoCevevLfo8nO2uX_0E-yGpdbA==; pxcts=c00cacff-f281-11ee-9fcc-5005b29d43ff; _pxhd=fDfFOXW4gQKeuKgxV8MZc2gM9CWMMrdOZR/AxH5-FYYytSio5mEZlbWeWgJR8riOOFt50qzvO/wOo5evPNn4eA==:WaTE8dn0r3Bqh2HOe0-hUHTvPgwrH7RqNVdw6IO2VKay4k9LY0d82M-f4Eyb/BKDbFb1JMkBruokPEeGwZSpIZA0-PS8yECd-GLHQy0cSIs=; _gid=GA1.2.1801026991.1712234960; _pin_unauth=dWlkPU1XSmtOak0wTnprdE1USXdZUzAwTWpjM0xUbG1OVGt0TnpobE56WTRNV1U0T0dFeg; __attentive_dv=1; _sctr=1%7C1712185200000; __cq_seg=0~-0.46!1~-0.34!2~0.32!3~0.05!4~0.28!5~0.33!6~0.29!7~-0.09!8~0.32!9~-0.43; _scid_r=c6239578-af94-4e9b-8bcc-c336872e4ed8; __cq_bc=%7B%22bdcn-USSkechers%22%3A%5B%7B%22id%22%3A%22216601%22%2C%22type%22%3A%22vgroup%22%2C%22alt_id%22%3A%22216601_NVOR%22%7D%2C%7B%22id%22%3A%22216602%22%2C%22type%22%3A%22vgroup%22%2C%22alt_id%22%3A%22216602_CCOR%22%7D%2C%7B%22id%22%3A%22136542%22%2C%22type%22%3A%22vgroup%22%2C%22alt_id%22%3A%22136542_BBK%22%7D%2C%7B%22id%22%3A%22177190%22%2C%22type%22%3A%22vgroup%22%2C%22alt_id%22%3A%22177190_WHT%22%7D%5D%7D; _ga=GA1.2.1403589783.1710483729; _uetsid=c3a51770f28111ee893735cca153fae2; _uetvid=5ca9a790e29411ee92fd53ef23222712; __rutma=45123878-s1-k4-42-1p-995o6bplm96ze14h9iox-1710483734576.1712234964748.1712236820138.10.72.6; _px3=12841dcd877e68018c7ca770310fd3b5c49758a7c8b70b9708796d80039a05a4:vuutn5J9JqOAp0o8nozgr1DD0H38UQOr/Asg44kr4pIIk6BLklbDnz5gVdHr/4UCI+eKaZDpxwmklB0FFA2Y3Q==:1000:5zBuEMb7uxnwKRqYQNAi/iFo9X/8KJOwdSYYNYJlV0Dsphrqqt8keOn9h+gfudqZXgx62qwgWUuWdyf7xBo6wAdZrMwlFmCmRqqX5IP0vZbukXAObv+1lHo7yCdx4giiF0xeD1AjjiXGaTOdJw9cIx5emDhipKji2Y/oki/L+UtfTRPaOuIIWvRgFtxoLRb8//vL5Ae/1drkwqyVsQVByRWnhoo7sTW2BnkCq8dXS30=; __cf_bm=aRCrU7cnuFywYjSeN0hTtYJK3DN0IA.9woZ_5RQL6S8-1712240595-1.0.1.1-Yc0j8Sl1607NnoqhPx6rGb_TnAUF4buk67exBs4hFiyVOmOkLmlfBO1BofKuZ7N55aNiAYmevS3Peo4O56nVfg; _ga_XZTV9LQ9DQ=GS1.1.1712240671.9.0.1712240680.51.0.0; __rpckx=0!eyJ0NyI6eyI3MSI6MTcxMjIzNzc4MDM4M30sInQ3diI6eyI3MSI6MTcxMjI0MTIxNTgxMX19; QuantumMetricSessionID=13ebeb4f79233420ba441bf0c7b4993b',
            'Pragma': 'no-cache',
            #'Referer': 'https://www.skechers.com/men/shoes/',
            'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': ua.random
        }
        for category, cat_url in self.cat_urls.items():
            yield scrapy.Request(url=cat_url, headers=headers, callback=self.parse, meta={'category': category, 'cat_url': cat_url, 'page': self.page})


    def parse(self, response):
        category = response.meta['category']
        cat_url = response.meta['cat_url']
        page = response.meta['page']
        links = response.xpath('//a[@class="link c-product-tile__title "]/@href')
        for link in links:
            url = link.get()
            url = self.main_url + url
            
            #print("#####################################")
            #print(url)
            yield scrapy.Request(url=url, headers=response.request.headers, callback=self.parse_product, meta={'category': category, 'url': url, 'page': page}) #'VendorCode': vendor_code})

        #NEXT PAGE
        next_page_url = response.xpath('//div[@class="show-more"]/div[@class="text-center"]/a/@href').get()
        if next_page_url:
            page = page + 1
            yield scrapy.Request(url=next_page_url, headers=response.request.headers, callback=self.parse, meta={'category': category, 'cat_url': cat_url, 'page': page})


    def parse_product(self, response):
        item = ProductItemSkechers()
        category = response.meta['category']
        url = response.meta['url']
        title = response.xpath("//h1[@class='c-product-details__product-name product-name']/text()").get()
        sub_category = response.xpath('//ol[@class="c-breadcrumbs breadcrumb"]/li[last()]/text()').get()
        price = response.xpath("//span[@class='sales ']/span[@class='value']/text()").get()
        rating = response.xpath("//section[@class='pr-review-snapshot-snippets']//div[@class='pr-snippet-rating-decimal']/text()").get()
        sku = re.search(r'/(\d+)_\w+\.html$', url).group(1) if re.search(r'/(\d+)_\w+\.html$', url) else None
        #comment = response.xpath('//p[@class="pr-rd-description-text"]/text()').get()

        yield {
            'ProductName': title,
            'URL': url

        }

        

            
        
        


        
        




