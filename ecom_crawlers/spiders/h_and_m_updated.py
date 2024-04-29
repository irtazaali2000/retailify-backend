import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemHandM
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import mysql.connector




class HandMSpider(Spider):
    name = 'h_and_m'
    allowed_domains = ['ae.hm.com', 'hgr051i5xn-dsn.algolia.net', 'api.bazaarvoice.com']
    main_url = 'https://ae.hm.com'
    products_api = 'https://hgr051i5xn-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)&x-algolia-application-id=HGR051I5XN&x-algolia-api-key=a2fdc9d456e5e714d8b654dfe1d8aed8'
    review_api = 'https://api.bazaarvoice.com/data/reviews.json?apiversion=5.4&passkey=caf5dGtwUGzhqIcWTSuBVjtbATWQvyCzylmXtoy02sbE8&locale=en_AE&filter=productid:{}&filter=contentlocale:en_KW,en_AE,en_SA,en_QA,en_EG,en_BH,ar_KW,ar_AE,ar_SA,ar_QA,ar_EG,ar_BH&Include=Products,Comments,Authors&Stats=Reviews&FilteredStats=Reviews&Limit=3&Offset=0&sort=IsFeatured:Desc,SubmissionTime:Desc,Helpfulness:Desc,Rating:Desc,Rating:Asc,HasPhotos:Desc'
    headers = {'Content-Type': 'application/json'}
    #body = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters={}&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&analytics=true"}]}
    body_men_clothes = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3ABag%22%2C%22attr_presentation_product_type.en%3ABeanie%22%2C%22attr_presentation_product_type.en%3ABelt%22%2C%22attr_presentation_product_type.en%3ABlazer%22%2C%22attr_presentation_product_type.en%3ABracelet%22%2C%22attr_presentation_product_type.en%3ABriefs%22%2C%22attr_presentation_product_type.en%3ACap%22%2C%22attr_presentation_product_type.en%3ACard%20holder%22%2C%22attr_presentation_product_type.en%3ACardigan%22%2C%22attr_presentation_product_type.en%3ACoat%22%2C%22attr_presentation_product_type.en%3AFashion%20scarf%22%2C%22attr_presentation_product_type.en%3AGilet%22%2C%22attr_presentation_product_type.en%3AGloves%22%2C%22attr_presentation_product_type.en%3AHat%22%2C%22attr_presentation_product_type.en%3AHeadband%22%2C%22attr_presentation_product_type.en%3AJacket%22%2C%22attr_presentation_product_type.en%3AJeans%22%2C%22attr_presentation_product_type.en%3AJumper%22%2C%22attr_presentation_product_type.en%3AKnitted%20hat%22%2C%22attr_presentation_product_type.en%3ALeggings%22%2C%22attr_presentation_product_type.en%3ALong%20johns%22%2C%22attr_presentation_product_type.en%3AMens%20briefs%22%2C%22attr_presentation_product_type.en%3ANecklace%22%2C%22attr_presentation_product_type.en%3AOutdoor%20jacket%22%2C%22attr_presentation_product_type.en%3APyjamas%22%2C%22attr_presentation_product_type.en%3ARing%22%2C%22attr_presentation_product_type.en%3AScarf%22%2C%22attr_presentation_product_type.en%3AShirt%22%2C%22attr_presentation_product_type.en%3AShorts%22%2C%22attr_presentation_product_type.en%3ASocks%22%2C%22attr_presentation_product_type.en%3ASuit%20jacket%22%2C%22attr_presentation_product_type.en%3ASunglasses%22%2C%22attr_presentation_product_type.en%3ASweatband%22%2C%22attr_presentation_product_type.en%3ASweatshirt%22%2C%22attr_presentation_product_type.en%3ASwim%20shorts%22%2C%22attr_presentation_product_type.en%3AT-shirt%22%2C%22attr_presentation_product_type.en%3ATie%22%2C%22attr_presentation_product_type.en%3ATie%20clip%22%2C%22attr_presentation_product_type.en%3ATop%22%2C%22attr_presentation_product_type.en%3ATrousers%22%2C%22attr_presentation_product_type.en%3AWaist%20coat%22%2C%22attr_presentation_product_type.en%3AWater%20bottle%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl2%3A%20%22Men%20%3E%20Shop%20By%20Product%20%3E%20View%20All%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22men__shop_by_product__view_all%22%2C%22men__shop_by_product%22%2C%22men%22%2C%22web__men%22%2C%22web__men__shop_by_product%22%2C%22web__men__shop_by_product__view_all%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl2%3A%20%22Men%20%3E%20Shop%20By%20Product%20%3E%20View%20All%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22men__shop_by_product__view_all%22%2C%22men__shop_by_product%22%2C%22men%22%2C%22web__men%22%2C%22web__men__shop_by_product%22%2C%22web__men__shop_by_product__view_all%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    body_men_shoes = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AShoes%22%2C%22attr_presentation_product_type.en%3ASlippers%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl2%3A%20%22Men%20%3E%20Shop%20By%20Product%20%3E%20View%20All%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22men__shop_by_product__view_all%22%2C%22men__shop_by_product%22%2C%22men%22%2C%22web__men%22%2C%22web__men__shop_by_product%22%2C%22web__men__shop_by_product__view_all%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl2%3A%20%22Men%20%3E%20Shop%20By%20Product%20%3E%20View%20All%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22men__shop_by_product__view_all%22%2C%22men__shop_by_product%22%2C%22men%22%2C%22web__men%22%2C%22web__men__shop_by_product%22%2C%22web__men__shop_by_product__view_all%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    body_women_clothes = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AAlice%20headband%22%2C%22attr_presentation_product_type.en%3AApplicator%22%2C%22attr_presentation_product_type.en%3ABag%22%2C%22attr_presentation_product_type.en%3ABath%20bomb%22%2C%22attr_presentation_product_type.en%3ABath%20fizzer%22%2C%22attr_presentation_product_type.en%3ABeanie%22%2C%22attr_presentation_product_type.en%3ABelt%22%2C%22attr_presentation_product_type.en%3ABikini%20bottoms%22%2C%22attr_presentation_product_type.en%3ABikini%20top%22%2C%22attr_presentation_product_type.en%3ABlazer%22%2C%22attr_presentation_product_type.en%3ABlouse%22%2C%22attr_presentation_product_type.en%3ABlusher%22%2C%22attr_presentation_product_type.en%3ABody%22%2C%22attr_presentation_product_type.en%3ABody%20brush%22%2C%22attr_presentation_product_type.en%3ABody%20jewellery%22%2C%22attr_presentation_product_type.en%3ABodysuit%22%2C%22attr_presentation_product_type.en%3ABra%22%2C%22attr_presentation_product_type.en%3ABra%20accessories%22%2C%22attr_presentation_product_type.en%3ABracelet%22%2C%22attr_presentation_product_type.en%3ABriefs%22%2C%22attr_presentation_product_type.en%3ABubble%20bath%22%2C%22attr_presentation_product_type.en%3ABustier%22%2C%22attr_presentation_product_type.en%3ACaftan%22%2C%22attr_presentation_product_type.en%3ACap%22%2C%22attr_presentation_product_type.en%3ACardigan%22%2C%22attr_presentation_product_type.en%3ACoat%22%2C%22attr_presentation_product_type.en%3AComb%22%2C%22attr_presentation_product_type.en%3ACorset%22%2C%22attr_presentation_product_type.en%3ADress%22%2C%22attr_presentation_product_type.en%3ADressing%20gown%22%2C%22attr_presentation_product_type.en%3AEarphone%20case%22%2C%22attr_presentation_product_type.en%3AEarrings%22%2C%22attr_presentation_product_type.en%3AEyebrow%20pencil%22%2C%22attr_presentation_product_type.en%3AEyebrow%20pomade%22%2C%22attr_presentation_product_type.en%3AEyebrow%20powder%22%2C%22attr_presentation_product_type.en%3AEyeshadow%22%2C%22attr_presentation_product_type.en%3AFace%20cleansing%20sponge%22%2C%22attr_presentation_product_type.en%3AFacial%20cleanser%22%2C%22attr_presentation_product_type.en%3AFacial%20cleansing%20pad%22%2C%22attr_presentation_product_type.en%3AFalse%20eyelashes%22%2C%22attr_presentation_product_type.en%3AFashion%20scarf%22%2C%22attr_presentation_product_type.en%3AFoundation%22%2C%22attr_presentation_product_type.en%3AGilet%22%2C%22attr_presentation_product_type.en%3AHair%20band%22%2C%22attr_presentation_product_type.en%3AHair%20brush%22%2C%22attr_presentation_product_type.en%3AHair%20claw%22%2C%22attr_presentation_product_type.en%3AHair%20clips%22%2C%22attr_presentation_product_type.en%3AHair%20elastic%22%2C%22attr_presentation_product_type.en%3AHat%22%2C%22attr_presentation_product_type.en%3AHeadband%22%2C%22attr_presentation_product_type.en%3AHighlighter%22%2C%22attr_presentation_product_type.en%3AJacket%22%2C%22attr_presentation_product_type.en%3AJeans%22%2C%22attr_presentation_product_type.en%3AJumper%22%2C%22attr_presentation_product_type.en%3AJumpsuit%22%2C%22attr_presentation_product_type.en%3AKnickers%22%2C%22attr_presentation_product_type.en%3ALeggings%22%2C%22attr_presentation_product_type.en%3ALip%20colour%22%2C%22attr_presentation_product_type.en%3ALip%20gloss%22%2C%22attr_presentation_product_type.en%3ALip%20pencil%22%2C%22attr_presentation_product_type.en%3ALipstick%22%2C%22attr_presentation_product_type.en%3AMakeup%20bag%22%2C%22attr_presentation_product_type.en%3AMakeup%20brush%22%2C%22attr_presentation_product_type.en%3AMakeup%20highlighter%22%2C%22attr_presentation_product_type.en%3AMakeup%20sponge%22%2C%22attr_presentation_product_type.en%3AMassage%20tool%22%2C%22attr_presentation_product_type.en%3ANail%20polish%22%2C%22attr_presentation_product_type.en%3ANecklace%22%2C%22attr_presentation_product_type.en%3ANight%20dress%22%2C%22attr_presentation_product_type.en%3ANipple%20covers%22%2C%22attr_presentation_product_type.en%3APlaysuit%22%2C%22attr_presentation_product_type.en%3APowder%22%2C%22attr_presentation_product_type.en%3APyjama%20bottoms%22%2C%22attr_presentation_product_type.en%3APyjamas%22%2C%22attr_presentation_product_type.en%3ARing%22%2C%22attr_presentation_product_type.en%3ARoller%22%2C%22attr_presentation_product_type.en%3ARoom%20fragrance%22%2C%22attr_presentation_product_type.en%3AScarf%22%2C%22attr_presentation_product_type.en%3AShirt%22%2C%22attr_presentation_product_type.en%3AShorts%22%2C%22attr_presentation_product_type.en%3ASkirt%22%2C%22attr_presentation_product_type.en%3ASmartphone%20case%22%2C%22attr_presentation_product_type.en%3ASocks%22%2C%22attr_presentation_product_type.en%3ASuit%20jacket%22%2C%22attr_presentation_product_type.en%3ASunglasses%22%2C%22attr_presentation_product_type.en%3ASuspender%20belt%22%2C%22attr_presentation_product_type.en%3ASweatshirt%22%2C%22attr_presentation_product_type.en%3ASwim%20top%22%2C%22attr_presentation_product_type.en%3ASwimsuit%22%2C%22attr_presentation_product_type.en%3AT-shirt%22%2C%22attr_presentation_product_type.en%3ATights%22%2C%22attr_presentation_product_type.en%3ATop%22%2C%22attr_presentation_product_type.en%3ATowel%22%2C%22attr_presentation_product_type.en%3ATrousers%22%2C%22attr_presentation_product_type.en%3ATunic%22%2C%22attr_presentation_product_type.en%3AUnder%20dress%22%2C%22attr_presentation_product_type.en%3AWaist%20coat%22%2C%22attr_presentation_product_type.en%3AWash%20bag%22%2C%22attr_presentation_product_type.en%3AWash%20sponge%22%2C%22attr_presentation_product_type.en%3AWomens%20briefs%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Women%20%3E%20Shop%20By%20Product%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22women__shop_by_product%22%2C%22women%22%2C%22web__women%22%2C%22web__women__shop_by_product%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Women%20%3E%20Shop%20By%20Product%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22women__shop_by_product%22%2C%22women%22%2C%22web__women%22%2C%22web__women__shop_by_product%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    body_women_shoes = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AShoes%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Women%20%3E%20Shop%20By%20Product%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22women__shop_by_product%22%2C%22women%22%2C%22web__women%22%2C%22web__women__shop_by_product%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Women%20%3E%20Shop%20By%20Product%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22women__shop_by_product%22%2C%22women%22%2C%22web__women%22%2C%22web__women__shop_by_product%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    
    body_girl_clothes = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AAll%20in%20one%20suit%22%2C%22attr_presentation_product_type.en%3ABaby%20bib%22%2C%22attr_presentation_product_type.en%3ABaby%20bodysuit%22%2C%22attr_presentation_product_type.en%3ABaby%20scarf%22%2C%22attr_presentation_product_type.en%3ABaby%20sleeping%20bag%22%2C%22attr_presentation_product_type.en%3ABag%22%2C%22attr_presentation_product_type.en%3ABeanie%22%2C%22attr_presentation_product_type.en%3ABib-style%20neck%20warmer%22%2C%22attr_presentation_product_type.en%3ABikini%20bottoms%22%2C%22attr_presentation_product_type.en%3ABloomers%22%2C%22attr_presentation_product_type.en%3ABlouse%22%2C%22attr_presentation_product_type.en%3ABody%22%2C%22attr_presentation_product_type.en%3ABodysuit%22%2C%22attr_presentation_product_type.en%3ACap%22%2C%22attr_presentation_product_type.en%3ACardigan%22%2C%22attr_presentation_product_type.en%3ACoat%22%2C%22attr_presentation_product_type.en%3ACollar%22%2C%22attr_presentation_product_type.en%3ACostume%22%2C%22attr_presentation_product_type.en%3ACostume%20party%20accessories%22%2C%22attr_presentation_product_type.en%3ADress%22%2C%22attr_presentation_product_type.en%3AFabric%20comb%22%2C%22attr_presentation_product_type.en%3AFancy%20dress%20costume%22%2C%22attr_presentation_product_type.en%3AGilet%22%2C%22attr_presentation_product_type.en%3AHat%22%2C%22attr_presentation_product_type.en%3AJacket%22%2C%22attr_presentation_product_type.en%3AJeans%22%2C%22attr_presentation_product_type.en%3AJumper%22%2C%22attr_presentation_product_type.en%3AJumpsuit%22%2C%22attr_presentation_product_type.en%3AKnickers%22%2C%22attr_presentation_product_type.en%3AKnitted%20hat%22%2C%22attr_presentation_product_type.en%3ALaundry%20bag%22%2C%22attr_presentation_product_type.en%3ALeggings%22%2C%22attr_presentation_product_type.en%3AMittens%22%2C%22attr_presentation_product_type.en%3APyjama%20jumpsuit%22%2C%22attr_presentation_product_type.en%3APyjamas%22%2C%22attr_presentation_product_type.en%3AShirt%22%2C%22attr_presentation_product_type.en%3AShorts%22%2C%22attr_presentation_product_type.en%3ASkirt%22%2C%22attr_presentation_product_type.en%3ASleepsuit%22%2C%22attr_presentation_product_type.en%3ASlippers%22%2C%22attr_presentation_product_type.en%3ASocks%22%2C%22attr_presentation_product_type.en%3ASoft%20toy%22%2C%22attr_presentation_product_type.en%3ASunglasses%22%2C%22attr_presentation_product_type.en%3ASweatshirt%22%2C%22attr_presentation_product_type.en%3ASwim%20shorts%22%2C%22attr_presentation_product_type.en%3ASwim%20top%22%2C%22attr_presentation_product_type.en%3ASwimsuit%22%2C%22attr_presentation_product_type.en%3AT-shirt%22%2C%22attr_presentation_product_type.en%3ATights%22%2C%22attr_presentation_product_type.en%3ATop%22%2C%22attr_presentation_product_type.en%3AToy%22%2C%22attr_presentation_product_type.en%3ATrousers%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Baby%20%3E%20Baby%20Girls%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22baby__baby_girls%22%2C%22baby%22%2C%22web__baby%22%2C%22web__baby__baby_girls%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Baby%20%3E%20Baby%20Girls%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22baby__baby_girls%22%2C%22baby%22%2C%22web__baby%22%2C%22web__baby__baby_girls%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    body_girl_shoes = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AShoes%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Baby%20%3E%20Baby%20Girls%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22baby__baby_girls%22%2C%22baby%22%2C%22web__baby%22%2C%22web__baby__baby_girls%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Baby%20%3E%20Baby%20Girls%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22baby__baby_girls%22%2C%22baby%22%2C%22web__baby%22%2C%22web__baby__baby_girls%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    
    body_boys_clothes = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AAll%20in%20one%20suit%22%2C%22attr_presentation_product_type.en%3ABaby%20bib%22%2C%22attr_presentation_product_type.en%3ABaby%20bodysuit%22%2C%22attr_presentation_product_type.en%3ABaby%20scarf%22%2C%22attr_presentation_product_type.en%3ABaby%20sleeping%20bag%22%2C%22attr_presentation_product_type.en%3ABeanie%22%2C%22attr_presentation_product_type.en%3ABib-style%20neck%20warmer%22%2C%22attr_presentation_product_type.en%3ABloomers%22%2C%22attr_presentation_product_type.en%3ABlouse%22%2C%22attr_presentation_product_type.en%3ABody%22%2C%22attr_presentation_product_type.en%3ABodysuit%22%2C%22attr_presentation_product_type.en%3ABoiler%20suit%22%2C%22attr_presentation_product_type.en%3ACap%22%2C%22attr_presentation_product_type.en%3ACardigan%22%2C%22attr_presentation_product_type.en%3ACollar%22%2C%22attr_presentation_product_type.en%3ACostume%22%2C%22attr_presentation_product_type.en%3ACostume%20party%20accessories%22%2C%22attr_presentation_product_type.en%3ADress%22%2C%22attr_presentation_product_type.en%3AGilet%22%2C%22attr_presentation_product_type.en%3AHat%22%2C%22attr_presentation_product_type.en%3AJacket%22%2C%22attr_presentation_product_type.en%3AJeans%22%2C%22attr_presentation_product_type.en%3AJumper%22%2C%22attr_presentation_product_type.en%3AJumpsuit%22%2C%22attr_presentation_product_type.en%3AKnitted%20hat%22%2C%22attr_presentation_product_type.en%3ALeggings%22%2C%22attr_presentation_product_type.en%3AMittens%22%2C%22attr_presentation_product_type.en%3APyjama%20jumpsuit%22%2C%22attr_presentation_product_type.en%3APyjamas%22%2C%22attr_presentation_product_type.en%3AShirt%22%2C%22attr_presentation_product_type.en%3AShorts%22%2C%22attr_presentation_product_type.en%3ASkirt%22%2C%22attr_presentation_product_type.en%3ASleepsuit%22%2C%22attr_presentation_product_type.en%3ASocks%22%2C%22attr_presentation_product_type.en%3ASoft%20toy%22%2C%22attr_presentation_product_type.en%3ASunglasses%22%2C%22attr_presentation_product_type.en%3ASweatshirt%22%2C%22attr_presentation_product_type.en%3ASwim%20shorts%22%2C%22attr_presentation_product_type.en%3ASwim%20top%22%2C%22attr_presentation_product_type.en%3ASwimsuit%22%2C%22attr_presentation_product_type.en%3AT-shirt%22%2C%22attr_presentation_product_type.en%3ATights%22%2C%22attr_presentation_product_type.en%3ATop%22%2C%22attr_presentation_product_type.en%3ATowel%22%2C%22attr_presentation_product_type.en%3AToy%22%2C%22attr_presentation_product_type.en%3ATrousers%22%2C%22attr_presentation_product_type.en%3AWaist%20coat%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Baby%20%3E%20Baby%20Boys%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22baby__baby_boys%22%2C%22baby%22%2C%22web__baby%22%2C%22web__baby__baby_boys%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Baby%20%3E%20Baby%20Boys%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22baby__baby_boys%22%2C%22baby%22%2C%22web__baby%22%2C%22web__baby__baby_boys%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    body_boys_shoes = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AShoes%22%2C%22attr_presentation_product_type.en%3ASlippers%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Baby%20%3E%20Baby%20Boys%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22baby__baby_boys%22%2C%22baby%22%2C%22web__baby%22%2C%22web__baby__baby_boys%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Baby%20%3E%20Baby%20Boys%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22baby__baby_boys%22%2C%22baby%22%2C%22web__baby%22%2C%22web__baby__baby_boys%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    
    body_kids_girls_clothes_2_8 = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AAlice%20headband%22%2C%22attr_presentation_product_type.en%3ABag%22%2C%22attr_presentation_product_type.en%3ABeanie%22%2C%22attr_presentation_product_type.en%3ABelt%22%2C%22attr_presentation_product_type.en%3ABikini%20bottoms%22%2C%22attr_presentation_product_type.en%3ABikini%20top%22%2C%22attr_presentation_product_type.en%3ABlazer%22%2C%22attr_presentation_product_type.en%3ABlouse%22%2C%22attr_presentation_product_type.en%3ABodysuit%22%2C%22attr_presentation_product_type.en%3ABolero%22%2C%22attr_presentation_product_type.en%3ABracelet%22%2C%22attr_presentation_product_type.en%3ACap%22%2C%22attr_presentation_product_type.en%3ACardigan%22%2C%22attr_presentation_product_type.en%3ACoat%22%2C%22attr_presentation_product_type.en%3ACostume%22%2C%22attr_presentation_product_type.en%3ADress%22%2C%22attr_presentation_product_type.en%3ADressing%20gown%22%2C%22attr_presentation_product_type.en%3AEarmuffs%22%2C%22attr_presentation_product_type.en%3AGilet%22%2C%22attr_presentation_product_type.en%3AGloves%22%2C%22attr_presentation_product_type.en%3AHair%20clips%22%2C%22attr_presentation_product_type.en%3AHair%20elastic%22%2C%22attr_presentation_product_type.en%3AHat%22%2C%22attr_presentation_product_type.en%3AJacket%22%2C%22attr_presentation_product_type.en%3AJeans%22%2C%22attr_presentation_product_type.en%3AJumper%22%2C%22attr_presentation_product_type.en%3AJumpsuit%22%2C%22attr_presentation_product_type.en%3AKnickers%22%2C%22attr_presentation_product_type.en%3ALeggings%22%2C%22attr_presentation_product_type.en%3ALunch%20box%22%2C%22attr_presentation_product_type.en%3ANecklace%22%2C%22attr_presentation_product_type.en%3ANight%20dress%22%2C%22attr_presentation_product_type.en%3AOutdoor%20jacket%22%2C%22attr_presentation_product_type.en%3APencil%20case%22%2C%22attr_presentation_product_type.en%3APyjamas%22%2C%22attr_presentation_product_type.en%3ARing%22%2C%22attr_presentation_product_type.en%3AScarf%22%2C%22attr_presentation_product_type.en%3AShirt%22%2C%22attr_presentation_product_type.en%3AShorts%22%2C%22attr_presentation_product_type.en%3ASkirt%22%2C%22attr_presentation_product_type.en%3ASocks%22%2C%22attr_presentation_product_type.en%3ASunglasses%22%2C%22attr_presentation_product_type.en%3ASweatshirt%22%2C%22attr_presentation_product_type.en%3ASwim%20top%22%2C%22attr_presentation_product_type.en%3ASwimsuit%22%2C%22attr_presentation_product_type.en%3AT-shirt%22%2C%22attr_presentation_product_type.en%3ATights%22%2C%22attr_presentation_product_type.en%3ATop%22%2C%22attr_presentation_product_type.en%3ATrousers%22%2C%22attr_presentation_product_type.en%3AUmbrella%22%2C%22attr_presentation_product_type.en%3AWater%20bottle%22%2C%22attr_presentation_product_type.en%3AWomens%20briefs%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Girls%202-8Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22kids__girls_28y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__girls_28y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Girls%202-8Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22kids__girls_28y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__girls_28y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    body_kids_girls_shoes_2_8 = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AShoes%22%2C%22attr_presentation_product_type.en%3ASlippers%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Girls%202-8Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22kids__girls_28y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__girls_28y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Girls%202-8Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22kids__girls_28y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__girls_28y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    body_kids_boys_clothes_2_8 = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AAll%20in%20one%20suit%22%2C%22attr_presentation_product_type.en%3ABag%22%2C%22attr_presentation_product_type.en%3ABeanie%22%2C%22attr_presentation_product_type.en%3ABelt%22%2C%22attr_presentation_product_type.en%3ABlazer%22%2C%22attr_presentation_product_type.en%3ABlouse%22%2C%22attr_presentation_product_type.en%3ABowtie%22%2C%22attr_presentation_product_type.en%3ABracelet%22%2C%22attr_presentation_product_type.en%3ABriefs%22%2C%22attr_presentation_product_type.en%3ACap%22%2C%22attr_presentation_product_type.en%3ACardigan%22%2C%22attr_presentation_product_type.en%3ACostume%22%2C%22attr_presentation_product_type.en%3ADressing%20gown%22%2C%22attr_presentation_product_type.en%3AGilet%22%2C%22attr_presentation_product_type.en%3AGloves%22%2C%22attr_presentation_product_type.en%3AHat%22%2C%22attr_presentation_product_type.en%3AJacket%22%2C%22attr_presentation_product_type.en%3AJeans%22%2C%22attr_presentation_product_type.en%3AJumper%22%2C%22attr_presentation_product_type.en%3AJumpsuit%22%2C%22attr_presentation_product_type.en%3ALeggings%22%2C%22attr_presentation_product_type.en%3ALong%20johns%22%2C%22attr_presentation_product_type.en%3AMens%20briefs%22%2C%22attr_presentation_product_type.en%3APencil%20case%22%2C%22attr_presentation_product_type.en%3APyjamas%22%2C%22attr_presentation_product_type.en%3AScarf%22%2C%22attr_presentation_product_type.en%3AShirt%22%2C%22attr_presentation_product_type.en%3AShorts%22%2C%22attr_presentation_product_type.en%3ASocks%22%2C%22attr_presentation_product_type.en%3ASuit%20jacket%22%2C%22attr_presentation_product_type.en%3ASunglasses%22%2C%22attr_presentation_product_type.en%3ASweatshirt%22%2C%22attr_presentation_product_type.en%3ASwim%20shorts%22%2C%22attr_presentation_product_type.en%3ASwim%20top%22%2C%22attr_presentation_product_type.en%3ASwimsuit%22%2C%22attr_presentation_product_type.en%3AT-shirt%22%2C%22attr_presentation_product_type.en%3ATie%22%2C%22attr_presentation_product_type.en%3ATop%22%2C%22attr_presentation_product_type.en%3ATrousers%22%2C%22attr_presentation_product_type.en%3AUmbrella%22%2C%22attr_presentation_product_type.en%3AWaist%20coat%22%2C%22attr_presentation_product_type.en%3AWater%20bottle%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Boys%202-8Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22kids__boys_28y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__boys_28y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Boys%202-8Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22kids__boys_28y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__boys_28y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    body_kids_boys_shoes_2_8 = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AShoes%22%2C%22attr_presentation_product_type.en%3ASlippers%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Boys%202-8Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22kids__boys_28y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__boys_28y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Boys%202-8Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22kids__boys_28y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__boys_28y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}

    body_kids_girls_clothes_9_14 = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AAlice%20headband%22%2C%22attr_presentation_product_type.en%3ABag%22%2C%22attr_presentation_product_type.en%3ABeanie%22%2C%22attr_presentation_product_type.en%3ABelt%22%2C%22attr_presentation_product_type.en%3ABlazer%22%2C%22attr_presentation_product_type.en%3ABlouse%22%2C%22attr_presentation_product_type.en%3ABodysuit%22%2C%22attr_presentation_product_type.en%3ACap%22%2C%22attr_presentation_product_type.en%3ACardigan%22%2C%22attr_presentation_product_type.en%3ACostume%22%2C%22attr_presentation_product_type.en%3ADress%22%2C%22attr_presentation_product_type.en%3ADressing%20gown%22%2C%22attr_presentation_product_type.en%3AGilet%22%2C%22attr_presentation_product_type.en%3AGloves%22%2C%22attr_presentation_product_type.en%3AHat%22%2C%22attr_presentation_product_type.en%3AJacket%22%2C%22attr_presentation_product_type.en%3AJeans%22%2C%22attr_presentation_product_type.en%3AJumper%22%2C%22attr_presentation_product_type.en%3AJumpsuit%22%2C%22attr_presentation_product_type.en%3AKnickers%22%2C%22attr_presentation_product_type.en%3ALeggings%22%2C%22attr_presentation_product_type.en%3ANight%20dress%22%2C%22attr_presentation_product_type.en%3APyjama%20bottoms%22%2C%22attr_presentation_product_type.en%3APyjamas%22%2C%22attr_presentation_product_type.en%3AShirt%22%2C%22attr_presentation_product_type.en%3AShorts%22%2C%22attr_presentation_product_type.en%3ASkirt%22%2C%22attr_presentation_product_type.en%3ASocks%22%2C%22attr_presentation_product_type.en%3ASunglasses%22%2C%22attr_presentation_product_type.en%3ASweatshirt%22%2C%22attr_presentation_product_type.en%3AT-shirt%22%2C%22attr_presentation_product_type.en%3ATights%22%2C%22attr_presentation_product_type.en%3ATop%22%2C%22attr_presentation_product_type.en%3ATrousers%22%2C%22attr_presentation_product_type.en%3AWater%20bottle%22%2C%22attr_presentation_product_type.en%3AWomens%20briefs%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Girls%209-14Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22kids__girls_914y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__girls_914y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Girls%209-14Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22kids__girls_914y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__girls_914y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    body_kids_girls_shoes_9_14 = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AShoes%22%2C%22attr_presentation_product_type.en%3ASlippers%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Girls%209-14Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22kids__girls_914y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__girls_914y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Girls%209-14Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22kids__girls_914y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__girls_914y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    body_kids_boys_clothes_9_14 = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AAlice%20headband%22%2C%22attr_presentation_product_type.en%3ABag%22%2C%22attr_presentation_product_type.en%3ABeanie%22%2C%22attr_presentation_product_type.en%3ABelt%22%2C%22attr_presentation_product_type.en%3ABlazer%22%2C%22attr_presentation_product_type.en%3ABlouse%22%2C%22attr_presentation_product_type.en%3ABriefs%22%2C%22attr_presentation_product_type.en%3ACap%22%2C%22attr_presentation_product_type.en%3ACardigan%22%2C%22attr_presentation_product_type.en%3AFabric%20comb%22%2C%22attr_presentation_product_type.en%3AGilet%22%2C%22attr_presentation_product_type.en%3AGloves%22%2C%22attr_presentation_product_type.en%3AHat%22%2C%22attr_presentation_product_type.en%3AJacket%22%2C%22attr_presentation_product_type.en%3AJeans%22%2C%22attr_presentation_product_type.en%3AJumper%22%2C%22attr_presentation_product_type.en%3ALaundry%20bag%22%2C%22attr_presentation_product_type.en%3ALeggings%22%2C%22attr_presentation_product_type.en%3ALong%20johns%22%2C%22attr_presentation_product_type.en%3APyjamas%22%2C%22attr_presentation_product_type.en%3AShirt%22%2C%22attr_presentation_product_type.en%3AShorts%22%2C%22attr_presentation_product_type.en%3ASocks%22%2C%22attr_presentation_product_type.en%3ASuit%20jacket%22%2C%22attr_presentation_product_type.en%3ASunglasses%22%2C%22attr_presentation_product_type.en%3ASweatshirt%22%2C%22attr_presentation_product_type.en%3AT-shirt%22%2C%22attr_presentation_product_type.en%3ATie%22%2C%22attr_presentation_product_type.en%3ATop%22%2C%22attr_presentation_product_type.en%3ATrousers%22%2C%22attr_presentation_product_type.en%3AWaist%20coat%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Boys%209-14Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22kids__boys_914y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__boys_914y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Boys%209-14Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22kids__boys_914y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__boys_914y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}
    body_kids_boys_shoes_9_14 = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facetFilters=%5B%5B%22attr_presentation_product_type.en%3AShoes%22%2C%22attr_presentation_product_type.en%3ASlippers%22%5D%5D&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Boys%209-14Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22kids__boys_914y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__boys_914y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"},{"indexName":"hm_prod_ae_product_list","params":"analytics=true&clickAnalytics=false&facets=attr_presentation_product_type.en&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Kids%20%3E%20Boys%209-14Y%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&optionalFilters=null&page={}&ruleContexts=%5B%22kids__boys_914y%22%2C%22kids%22%2C%22web__kids%22%2C%22web__kids__boys_914y%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f"}]}

    body_home = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22H%26M%20HOME%20%3E%20Shop%20By%20Product%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22hm_home__shop_by_product%22%2C%22hm_home%22%2C%22web__hm_home%22%2C%22web__hm_home__shop_by_product%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"}]}
    body_beauty = {"requests":[{"indexName":"hm_prod_ae_product_list","params":"clickAnalytics=true&facets=%5B%22*%22%5D&filters=(stock%20%3E%200)%20AND%20(field_category_name.en.lvl1%3A%20%22Beauty%20%3E%20Beauty%20Products%22)&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&optionalFilters=null&page={}&ruleContexts=%5B%22beauty__beauty_products%22%2C%22beauty%22%2C%22web__beauty%22%2C%22web__beauty__beauty_products%22%5D&userToken=anonymous-14922401-0348-4bf5-b549-ae4fcd53660f&analytics=true"}]}

    
    #Just make page and category name dynamic in body

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }
    
    page = 0
    count = 0
    
    
    categories = {
                    'Fashion': {
                        'Men Clothing': body_men_clothes,
                        'Men Shoes': body_men_shoes,
                        'Women Clothing': body_women_clothes,
                        'Women Shoes': body_women_shoes
                    },

                    'Baby & Kids': {
                        'Boys Clothing': body_boys_clothes,
                        'Boys Clothing': body_kids_boys_clothes_2_8,
                        'Boys Clothing': body_kids_boys_clothes_9_14,
                        'Boys Shoes': body_boys_shoes,
                        'Boys Shoes': body_kids_boys_shoes_2_8,
                        'Boys Shoes': body_kids_boys_shoes_9_14,
                        'Girls Clothing': body_girl_clothes,
                        'Girls Clothing': body_kids_girls_clothes_2_8,
                        'Girls Clothing': body_kids_girls_clothes_9_14,
                        'Girls Shoes': body_girl_shoes,
                        'Girls Shoes': body_kids_girls_shoes_2_8,
                        'Girls Shoes': body_kids_girls_shoes_9_14

                    },

                    'Home Appliances': {
                        'Home Appliances Accessories': body_home
                    },

                    'Personal Care & Beauty': {
                        'Makeup & Accessories': body_beauty
                    }
                }
    
    conn = mysql.connector.connect(
            # host='localhost',
            # user='root',
            # password='admin',
            # database='gb'
            host="mysqldb.cb2aesoymr8i.eu-west-2.rds.amazonaws.com",
            user="datapillar",
            password="4wIwdBmMSJ3BLBVCesJT",
            database="scrappers_db",
            port="3306"
        )
    cursor = conn.cursor(buffered=True)
    #visited_urls = set()

    def __init__(self, reviews='False', short_scraper="False", *args, **kwargs):
        super().__init__()

        self.reviews = reviews.lower() == 'true'
        self.short_scraper = short_scraper.lower() == 'true'
        catalogue_url = CATALOGUE_URL_T.format(self.name, self.short_scraper)
        categories_url = "{}{}".format(HOST, catalogue_url)
        raw_res = requests.get(categories_url).json()
    #     self.categories = raw_res.get('data', [])
        self.vendor_code = raw_res.get('VendorCode')

    def get_catalogue_code(self, catalogue_name):
        # Attempt to retrieve the catalog code and name from the database
        query_select = "SELECT CatalogueCode, CatalogueName FROM product_catalogue WHERE CatalogueName = %s"
        self.cursor.execute(query_select, (catalogue_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the catalog code exists, check if the name needs to be updated
            if result[1] != catalogue_name:
                update_query = "UPDATE product_catalogue SET CatalogueName = %s WHERE CatalogueCode = %s"
                self.cursor.execute(update_query, (catalogue_name, result[0]))
                self.conn.commit()  # Commit the transaction
                
            return result[0]
        else:
            # If the catalog code doesn't exist, insert it into the database
            insert_query = "INSERT INTO product_catalogue (CatalogueName) VALUES (%s)"
            self.cursor.execute(insert_query, (catalogue_name,))
            self.conn.commit()  # Commit the transaction
            
            # Retrieve the newly inserted catalog code and name
            self.cursor.execute(query_select, (catalogue_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None


    
    def get_category_code(self, category_name, catalogue_code):
        # Attempt to retrieve the category code and name from the database
        query_select = "SELECT CategoryCode, CategoryName FROM product_category WHERE CategoryName = %s"
        self.cursor.execute(query_select, (category_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the category code exists, check if the name needs to be updated
            if result[1] != category_name:
                update_query = "UPDATE product_category SET CategoryName = %s WHERE CategoryCode = %s"
                self.cursor.execute(update_query, (category_name, result[0]))
                self.conn.commit()  # Commit the transaction
            
            return result[0]
        else:
            # If the category code doesn't exist, insert it into the database
            insert_query = "INSERT INTO product_category (CategoryName, CatalogueCode_id) VALUES (%s, %s)"
            self.cursor.execute(insert_query, (category_name, catalogue_code))
            self.conn.commit()  # Commit the transaction
            
            # Retrieve the newly inserted category code and name
            self.cursor.execute(query_select, (category_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None

    def start_requests(self):
        for main_category, sub_categories in self.categories.items():
            for sub_category, body in sub_categories.items():
                catalogue_code = self.get_catalogue_code(main_category)  # Assuming you have this method implemented
                if catalogue_code:
                    print("########################################", sub_category)
                    modified_body = copy.deepcopy(body)
                    # Loop through each request and update the params with the new page number
                    for request in modified_body['requests']:
                        # Extract existing page number
                        params = request['params']
                        page_placeholder_index = params.find("&page=")
                        if page_placeholder_index != -1:
                            next_amp_index = params.find("&", page_placeholder_index + 1)
                            if next_amp_index != -1:
                                params = params[:page_placeholder_index] + "&page={}" + params[next_amp_index:]
                            else:
                                params = params[:page_placeholder_index] + "&page={}"

                        # Format the params with the new page number
                        request['params'] = params.format(self.page)

                    # Convert the modified body back to JSON
                    body = json.dumps(modified_body)
                    yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, callback=self.parse, meta={'category': main_category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'body': body, 'page': self.page})

    
    def parse(self, response):
        item = ProductItemHandM()
        vendor_code = self.vendor_code
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        catalogue_code = response.meta['catalogue_code']
        body = response.meta['body']
        print("Category: ", category)
        page = response.meta['page']
        data = json.loads(response.text)
        results = data.get('results', [])
        for result in results:
            hits = result.get('hits', [])
            if hits:
                for hit in hits:
                    item['SKU'] = hit.get('gtm', {}).get('gtm-product-sku')
                    item['ProductName'] = hit.get('gtm', {}).get('gtm-name')
                    item['BrandName'] = hit.get('gtm', {}).get('gtm-brand')
                    if not item['BrandName']:
                        item['BrandName'] = ''
                    item['CatalogueName'] = category
                    item['CategoryName'] = sub_category
                    
                    # category_list3 = hit.get('lhn_category', {}).get('en', {}).get('lvl3', [])
                    # if category_list3:
                    #     item['CategoryName'] = category_list3[0].split('>')[3]
                       
                    # else:
                    #     category_list2 = hit.get('lhn_category', {}).get('en', {}).get('lvl2', [])
                    #     if category_list2:
                    #         item['CategoryName'] = category_list2[0].split('>')[2]
               
                    #     else:
                    #         category_list1 = hit.get('lhn_category', {}).get('en', {}).get('lvl1', [])
                    #         if category_list1:
                    #             item['CategoryName'] = category_list1[0].split('>')[1]
   
                    #         else:
                    #             category_list0 = hit.get('lhn_category', {}).get('en', {}).get('lvl0', [])
                    #             if category_list0:
                    #                 item['CategoryName'] = category_list0[0].split('>')[0]
                    

                    # if not item['CategoryName']:
                    #     item['CategoryName'] = item['CatalogueName']



                    item['StockAvailability'] = hit.get('in_stock')
                    item['RatingValue'] = round(float(hit.get('attr_bv_average_overall_rating', {}).get('ar', 0)), 2)
                    item['MainImage'] = hit.get('media', [])
                    if item['MainImage']:
                        item['MainImage'] = item['MainImage'][0].get('url')
                    item['Offer'] = round(float(hit.get('gtm', {}).get('gtm-price')), 2)
                    item['RegularPrice'] = round(float(hit.get('gtm', {}).get('gtm-old-price')), 2)
                    if item['Offer'] == item['RegularPrice']:
                        item['Offer'] = 0

                    url = hit.get('url', {}).get('en')
                    item['URL'] = self.main_url + url

                    #item['page'] = page

                    item['BrandCode']= ''
                    item['ModelNumber']= ''
                    item['VendorCode']= vendor_code
                    #catalogue_code = response.meta['catalogue_code']
                    # item['CategoryName'] = item['CategoryName'].strip()
                    category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                    item['CatalogueCode']= catalogue_code
                    item['CategoryCode']= category_code
                    
                    self.count+=1
                    yield scrapy.Request(url=self.review_api.format(item['SKU']), dont_filter=False, headers=self.headers, callback=self.parse_review, meta={
                        'item': item,
                })
                
        print("Category = {}, Total Products = {} on Page = {}".format(category, self.count, page))
        page = page + 1      
        modified_body = json.loads(body)

        # Loop through each request and update the params with the new page number
        for request in modified_body['requests']:
            # Extract existing page number
            params = request['params']
            page_placeholder_index = params.find("&page=")
            if page_placeholder_index != -1:
                next_amp_index = params.find("&", page_placeholder_index + 1)
                if next_amp_index != -1:
                    params = params[:page_placeholder_index] + "&page={}" + params[next_amp_index:]
                else:
                    params = params[:page_placeholder_index] + "&page={}"

            # Format the params with the new page number
            request['params'] = params.format(page)

        # Convert the modified body back to JSON
        body = json.dumps(modified_body)
        yield scrapy.Request(url=self.products_api, method='POST', headers=self.headers, body=body, meta={'category':category, 'sub_category': sub_category, 'catalogue_code': catalogue_code, 'body': body, 'page':page})


    def parse_review(self, response):
        item = response.meta['item']
        item_reviews = []

        data = json.loads(response.text)
        item['RatingValue'] = round(float(data.get('Includes', {}).get('Products', {}).get(str(item['SKU']), {}).get('FilteredReviewStatistics', {}).get('AverageOverallRating', 0)), 2)
        reviews = data.get('Results', [])
        if reviews:
            for review in reviews:
                comment = review.get('ReviewText')
                source = review.get('SourceClient')
                comment_date = review.get('SubmissionTime', '')
                comment_date = datetime.strptime(comment_date, '%Y-%m-%dT%H:%M:%S.%f%z')
                comment_date = comment_date.strftime('%Y-%m-%d')
                rating = review.get('Rating')
                max_rating = round(float(review.get('RatingRange')), 2)

                review_data = {
                    'Comment': comment,
                    'Source': source,
                    'CommentDate': comment_date,
                    'rating': rating,
                    'max_rating': max_rating,
                    'average_rating': item['RatingValue']
                }
                item_reviews.append(review_data)
            item['reviews'] = item_reviews

        else:
            pass

        yield item