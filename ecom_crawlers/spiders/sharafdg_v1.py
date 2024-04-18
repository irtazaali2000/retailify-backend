# import re
# import requests
# from scrapy.spiders import Spider, CrawlSpider, Request
# import json
# from scrapy.selector import Selector
# import logging
# from datetime import datetime

# from ..settings import HOST, CATALOGUE_URL_T
# from ..items import ProductItemSharafDg
# from ecom_crawlers.utils import *
# from fake_useragent import UserAgent
# import scrapy
# import copy




# class SharafDGSpiderV1(Spider):
#     name = 'sharafdgv1'
#     allowed_domains = ['uae.sharafdg.com', '9khjlg93j1-dsn.algolia.net', 'js.testfreaks.com', 'd1le22hyhj2ui8.cloudfront.net']
#     #main_url = 'https://www.lifepharmacy.com/'
#     products_api = 'https://9khjlg93j1-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.24.9%3BJS%20Helper%202.23.2&x-algolia-application-id=9KHJLG93J1&x-algolia-api-key=e81d5b30a712bb28f0f1d2a52fc92dd0'
#     review_api_1 = 'https://d1le22hyhj2ui8.cloudfront.net/badge/sharafdg.com/reviews.json?key={}'
#     review_api_2 = 'https://js.testfreaks.com/badge/sharafdg.com/reviews.json?pid={}&type=user'
    
#     headers = {
#                'Content-Type': 'application/json',
#                'Referer': 'https://uae.sharafdg.com/'
#                 }
    
#     body = {"requests":[{"indexName":"products_index","params":"query=&hitsPerPage=48&maxValuesPerFacet=20&page={}&attributesToRetrieve=permalink%2Cpermalink_ar%2Cpost_id%2Cpost_title%2Cpost_title_ar%2Cmain_sku%2Ctaxonomies.taxonomies_hierarchical.product_cat%2Ctaxonomies_ar.product_cat%2Ctaxonomies.product_brand%2Ctaxonomies_ar.product_brand%2Cdiscount%2Cdiscount_val%2Cimages%2Cprice%2Csku%2Cpromotion_offer_json%2Cregular_price%2Csale_price%2Cin_stock%2Ctags%2Crating_reviews%2Ctags_ar&attributesToHighlight=post_title%2Cpost_title_ar&getRankingInfo=1&filters=post_status%3Apublish%20AND%20price%3E0%20AND%20archive%3A0%20AND%20in_stock%3A1%20%20AND%20taxonomies.erp_ver%3A2&clickAnalytics=true&facets=%5B%22tags.title%22%2C%22taxonomies.attr.Brand%22%2C%22inventory.store_availability%22%2C%22price%22%2C%22rating_reviews.rating%22%2C%22promotion_offer_json.seller_code%22%2C%22taxonomies.ED_Seller%22%2C%22promotion_offer_json.fulfilled_by%22%2C%22taxonomies.attr.Processor%22%2C%22taxonomies.attr.Screen%20Size%22%2C%22taxonomies.attr.Internal%20Memory%22%2C%22taxonomies.attr.Type%22%2C%22taxonomies.attr.Storage%20Size%22%2C%22taxonomies.attr.RAM%22%2C%22taxonomies.attr.Graphics%20Card%22%2C%22taxonomies.attr.Color%22%2C%22taxonomies.attr.OS%22%2C%22taxonomies.attr.Size%22%2C%22taxonomies.attr.Megapixel%22%2C%22taxonomies.attr.Capacity%22%2C%22taxonomies.attr.Loading%20Type%22%2C%22taxonomies.attr.Tonnage%22%2C%22taxonomies.attr.Compressor%20Type%22%2C%22taxonomies.attr.Star%20Rating%22%2C%22taxonomies.attr.Energy%20input%22%2C%22taxonomies.attr.Water%20Consumption%22%2C%22taxonomies.attr.Control%20Type%22%2C%22taxonomies.attr.Number%20of%20Channels%22%2C%22taxonomies.attr.Audio%20Output%22%2C%22taxonomies.attr.No%20of%20Burners%2FHobs%22%2C%22taxonomies.attr.HDMI%22%2C%22taxonomies.attr.Total%20Capacity%22%2C%22taxonomies.attr.Number%20of%20Doors%22%2C%22taxonomies.attr.Watches%20For%22%2C%22taxonomies.attr.Display%20Type%22%2C%22taxonomies.attr.Water%20Resistant%20Depth%20(m)%22%2C%22taxonomies.attr.Power%20Source%22%2C%22taxonomies.attr.Net%20Content%22%2C%22taxonomies.attr.Target%20Group%22%2C%22taxonomies.attr.Fragrance%20Type%22%2C%22taxonomies.attr.Noise%20Cancellation%20Headphone%22%2C%22taxonomies.attr.Built-in%20%2F%20Free-standing%22%2C%22taxonomies.attr.Built%20In%20%2F%20Free%20Standing%22%2C%22taxonomies.attr.Mode%22%2C%22taxonomies.attr.Series%22%2C%22taxonomies.attr.PEGI%2FESRB%22%2C%22taxonomies.attr.Lens%20Color%22%2C%22taxonomies.attr.Lens%20Type%22%2C%22taxonomies.attr.Frame%20Material%22%2C%22taxonomies.attr.Frame%20Shape%22%2C%22taxonomies.attr.Focal%20Length%20Range%22%2C%22taxonomies.attr.Aperture%20Range%22%2C%22taxonomies.attr.Filter%20Thread%22%2C%22taxonomies.attr.Effective%20Megapixel%22%2C%22taxonomies.attr.Resolution%22%2C%22taxonomies.attr.Aspect%20Ratio%22%2C%22taxonomies.attr.Functions%22%2C%22taxonomies.attr.Print%20Technology%22%2C%22taxonomies.attr.Scanning%20speed%20(color)%22%2C%22taxonomies.attr.Supported%20Memory%20Type%22%2C%22taxonomies.attr.Seating%20Capacity%22%2C%22taxonomies.attr.Unit%20Components%20Count%22%2C%22taxonomies.attr.Battery%20Capacity%22%2C%22taxonomies.attr.USB%20Output%22%2C%22taxonomies.attr.Unit%20Component%22%2C%22taxonomies.attr.Toys%20Type%22%2C%22taxonomies.attr.Fitness%20Equipments%20Type%22%2C%22taxonomies.attr.Miscellaneous%20Type%22%2C%22taxonomies.attr.Cookware%20Type%22%2C%22taxonomies.attr.Outdoor%20Products%20Type%22%2C%22taxonomies.attr.Tools%20Type%22%2C%22taxonomies.attr.Ideal%20For%22%2C%22taxonomies.attr.Age%20Group%22%2C%22taxonomies.seller_type%22%2C%22taxonomies.taxonomies_hierarchical.product_cat.lvl0%22%2C%22taxonomies.taxonomies_hierarchical.product_cat.lvl1%22%5D&tagFilters=&facetFilters=%5B%5B%22taxonomies.taxonomies_hierarchical.product_cat.lvl0%3A{}%22%5D%5D"},{"indexName":"products_index","params":"query=&hitsPerPage=1&maxValuesPerFacet=20&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&getRankingInfo=1&filters=post_status%3Apublish%20AND%20price%3E0%20AND%20archive%3A0%20AND%20in_stock%3A1%20%20AND%20taxonomies.erp_ver%3A2&clickAnalytics=true&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&facets=%5B%22taxonomies.taxonomies_hierarchical.product_cat.lvl0%22%5D"}]}

    

#     custom_settings = {
#         # 'DOWNLOAD_DELAY': 0.1,
#         # 'RETRY_TIMES': 3,
#         # 'DOWNLOAD_TIMEOUT': 1,
#         'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
#         #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
#     }

#     page = 0
#     count = 0
    
#     categories = {
#         'Mobile Phones and Tablets': 'Mobiles%20%26%20Tablets',
#         'Health Fitness Beauty': 'Health%2C%20Fitness%20%26%20Beauty',
#         'Computing': 'Computing',
#         'TV Video Audio': 'TV%2C%20Video%20%26%20Audio',
#         'Wearables and Smartwatches': 'Wearables%20%26%20Smartwatches',
#         'Home Kitchen Appliances': 'Home%20Appliances',
#         'Gaming': 'Gaming',
#         'Cameras Camcorders': 'Cameras%20%26%20Camcorders'
#             }

    
#     def start_requests(self):
#         for category, formatted_category in self.categories.items():
#             modified_body = copy.deepcopy(self.body)      
#             formatted_body = modified_body["requests"][0]["params"].format(self.page, formatted_category)
#             modified_body["requests"][0]["params"] = formatted_body
#             body = json.dumps(modified_body)
#             yield scrapy.Request(url=self.products_api, headers=self.headers, method='POST', body=body, callback=self.parse, meta={'category': category, 'formatted_category': formatted_category, 'page': self.page})

#     def parse(self, response):
#         category = response.meta['category']
#         formatted_category = response.meta['formatted_category']
#         page = response.meta['page']
#         data = json.loads(response.text)
#         results = data.get('results', [])[0]
#         hits = results.get('hits')
#         if hits:
#             for hit in hits:
#                 title = hit.get('post_title', '')
#                 sku = hit.get('main_sku', '')
#                 img = hit.get('images', '')
#                 url = hit.get('permalink', '')
#                 price_in_aed = hit.get('regular_price', 0)
#                 sale_price_in_aed = hit.get('sale_price', 0)
#                 if not sale_price_in_aed:
#                     sale_price_in_aed = 0
#                 brand = hit.get('taxonomies', {}).get('product_brand', [])[0]
#                 sub_categories_dict = hit.get('taxonomies', {}).get('taxonomies_hierarchical', {}).get('product_cat', {})
#                 if sub_categories_dict:
#                     last_lvl_key = sorted(sub_categories_dict.keys())[-1]  # Get the last key in the hierarchy
#                     sub_categories = sub_categories_dict[last_lvl_key] 
#                 else:
#                     sub_categories = ''

#                 in_stock = hit.get('in_stock', 1)
#                 discount_percentage = hit.get('discount', '')
#                 if not discount_percentage:
#                     discount_percentage = ''
                 
#                 discount_value = hit.get('discount_val', 0)
#                 if not discount_value:
#                     discount_value = 0
#                 rating = hit.get('rating_reviews', {})

#                 if rating:
#                     rating = rating.get('rating', 0)
#                     ReviewCount = rating.get('ReviewCount', 0)
#                 else:
#                     rating = 0
#                     ReviewCount = 0

                


#                 yield scrapy.Request(url=self.review_api_1.format(sku), callback=self.parse_pid, 
#                     meta={
#                     'title': title, 
#                     'sku': sku,
#                     'img': img,
#                     'url': url,
#                     'price_in_aed': price_in_aed,
#                     'sale_price_in_aed': sale_price_in_aed,
#                     'brand': brand,
#                     'sub_categories': sub_categories,
#                     'in_stock': in_stock,
#                     'discount_percentage': discount_percentage,
#                     'discount_value': discount_value,
#                     'rating': rating,
#                     'category': category,
#                     'page': page,
#                     'ReviewCount': ReviewCount
#                     })
          
#             #Next Page
#             page = page + 1
#             modified_body = copy.deepcopy(self.body)      
#             formatted_body = modified_body["requests"][0]["params"].format(page, formatted_category)
#             modified_body["requests"][0]["params"] = formatted_body
#             body = json.dumps(modified_body)
#             yield scrapy.Request(url=self.products_api, headers=self.headers, method='POST', body=body,  meta={'category': category, 'formatted_category': formatted_category, 'page': page})


#     def parse_pid(self, response):
#         item = ProductItemSharafDg()
#         item['title'] = response.meta['title']
#         item['sku'] = response.meta['sku']
#         item['img'] = response.meta['img']
#         item['url'] = response.meta['url']
#         item['price_in_aed'] = response.meta['price_in_aed']
#         item['sale_price_in_aed'] = response.meta['sale_price_in_aed']
#         item['brand'] = response.meta['brand']
#         item['sub_categories'] = response.meta['sub_categories']
#         item['in_stock'] = response.meta['in_stock']
#         item['discount_percentage'] = response.meta['discount_percentage']
#         item['discount_value'] = response.meta['discount_value']
#         item['rating'] = response.meta['rating']
#         item['review_text'] = ''
#         item['category'] = response.meta['category']
#         item['page'] = response.meta['page']
#         item['ReviewCount'] = response.meta['ReviewCount']

#         data = json.loads(response.text)
#         pid_url = data.get('user_review_url')
#         if pid_url:
#             pid_match_re = re.search(r'pid=(\d+)', pid_url)
#             if pid_match_re:
#                 pid = pid_match_re.group(1)
#                 yield scrapy.Request(url=self.review_api_2.format(pid), callback=self.parse_review, 
#                                                          meta={
#                                                             'title': item['title'], 
#                                                             'sku': item['sku'],
#                                                             'img': item['img'],
#                                                             'url': item['url'],
#                                                             'price_in_aed': item['price_in_aed'],
#                                                             'sale_price_in_aed': item['sale_price_in_aed'],
#                                                             'brand': item['brand'],
#                                                             'sub_categories': item['sub_categories'],
#                                                             'in_stock': item['in_stock'],
#                                                             'discount_percentage': item['discount_percentage'],
#                                                             'discount_value': item['discount_value'],
#                                                             'rating': item['rating'],
#                                                             'pid': pid,
#                                                             'category': item['category'],
#                                                             'page': item['page'],
#                                                             'ReviewCount': item['ReviewCount']
#                                                             })
#             else:
#                 print("PID not found in user_review_url: %s", pid_url)
#         else:
#             #print('user_review_url not found in response data.')
#             yield item

#     def parse_review(self, response):
#         item = ProductItemSharafDg()
#         item['ProductName'] = response.meta['title']
#         item['SKU'] = response.meta['sku']
#         item['MainImage'] = response.meta['img']
#         item['URL'] = response.meta['url']
#         item['RegularPrice'] = response.meta['price_in_aed']
#         item['Offer'] = response.meta['sale_price_in_aed']
#         item['BrandName'] = response.meta['brand']
#         item['CategoryName'] = response.meta['sub_categories']
#         item['StockAvailability'] = response.meta['in_stock']
#         #item['discount_percentage'] = response.meta['discount_percentage']
#         #item['discount_value'] = response.meta['discount_value']
#         item['RatingValue'] = response.meta['rating']
#         #item['pid'] = response.meta['pid']
#         item['CatalogueName'] = response.meta['category']
#         item['ReviewCount'] = response.meta['ReviewCount']
        
#         #item['page'] = response.meta['page']

#         data = json.loads(response.text)
#         reviews = data.get('reviews', [])
#         if reviews:
#             review = reviews[0]
#             item['review_text'] = review.get('extract', '')
#         else:
#             item['review_text'] = ''


#         yield item

        
        




