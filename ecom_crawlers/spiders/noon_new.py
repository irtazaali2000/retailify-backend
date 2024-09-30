import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemNoon
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import psycopg2
import os
from copy import deepcopy


class NoonSpider(Spider):
    name = 'noon'
    allowed_domains = ['noon.com']
    main_url = 'https://www.noon.com'
    url_product_template = 'https://www.noon.com/uae-en/{}/{}/p/'
    img_product_template = 'https://f.nooncdn.com/p/{}.jpg'
    review_url = 'https://www.noon.com/_svc/mp-trust-api/product-reviews/sku/list/'
    body = {
        "sku": "{}",
        "lang": "xx",
        "ratings": [1, 2, 3, 4, 5],
        "provideBreakdown": True,
        "page": 1,
        "perPage": 15,
        "sortFilter": "helpful",
        "imagesFilter": False
    }


    headers = {
        'authority': 'www.noon.com',
        'method': 'GET',
        'path': '/_svc/catalog/api/v3/u/electronics-and-mobiles/all-p-fbn-ae/?limit=50&page=0&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'scheme': 'https',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://www.noon.com/uae-en/electronics-and-mobiles/all-p-fbn-ae/?limit=50&page=3&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'X-Aby': '{"ipl_entrypoint_v2.enabled":1,"ipl_v2.enabled":1,"noon_pass.enabled":1,"otp_login.enabled":1,"pdp_bos.enabled":1,"pdp_flyout.flyout_value":0,"pp_entrypoint.enabled":1,"second_tab_screen.name":"dynamicTab"}',
        'X-Cms': 'v3',
        'X-Content': 'desktop',
        'X-Lat': '25.1998495',
        'X-Lng': '55.2715985',
        'X-Locale': 'en-ae',
        'X-Mp': 'noon',
        'X-Platform': 'web',
        'X-Visitor-Id': '3c2883ca-1b7f-454b-96f4-cbe9b90bc0db'
    }

    review_headers = {
    'authority': 'www.noon.com',
    'method': 'POST',
    'path': 'https://www.noon.com',
    #'path': '/_svc/catalog/api/v3/u/electronics-and-mobiles/all-p-fbn-ae/?limit=50&page=0&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    'scheme': 'https',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/json',
    #'Cookie': 'nloc=en-ae; visitor_id=3c2883ca-1b7f-454b-96f4-cbe9b90bc0db; _gcl_au=1.1.1385826969.1708068654; _ga=GA1.2.1968629218.1708068654; _fbp=fb.1.1708068654293.1845911762; _scid=066f7c4a-e8e7-464b-9391-07d9cf77d3ba; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22AHmwZChPEsw40oHXrnfv%22%7D; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3Anull%7D; _ym_uid=1708068656794109551; _ym_d=1708068656; _tt_enable_cookie=1; _ttp=dk024lX8-6qZxhog6-umXZWkwB2; __zlcmid=1KLmV9L8yUZ5bji; _gid=GA1.2.2093820198.1712149497; _sctr=1%7C1712098800000; review_lang=xx; x-available-ae=ecom; _clck=18plloi%7C2%7Cfkn%7C0%7C1507; bm_mi=1BD0DA255C892C7E4CEFC27DD1FCC9DC~YAAQHtYsF1IiLYqOAQAA4UTJpxdeooJorwOcZPwHNOCx8YOLVokWx2PGDb9RfAdlTThddtt0HU29exeUeVwGJTaHTiCP35/N1DrVhdJPSehtHRD9OP5NJtmSyATOA95Z5EvOe+FFLZUKFdkKOtuaqQMELRDxEY8RgSTXUkjqEi2NamzjTsyeHRNYdGFsxuI/mDiQYZfz4PredUb6SXX9OtyfVU+qXHLmb+WIiz5mAj5TcnN2fzvaym6wpksFM/YaVCw+B2B3REbrvYviPTUePemnRFCUAV/Gts9LEi0MvTyRT2CuF/oDwWmX0Hd1S4VG+zH2Yyj4JCatOJtKuxv7NxfnczgrLGSwLp5J0ljGclNGkja8ah1YJQ2o~1; ak_bmsc=7692BC37019E2CC063A252F821ED2797~000000000000000000000000000000~YAAQHtYsFwkkLYqOAQAAl1vJpxcNvXXcTGfAzS5ZASWYekmIoZ2/gbqGctTGE+TIWXKi1mV1CSfJDHOxUc0/GTtvA8oK2E0EaUCLw7IRGzdoGGYIMOQhvFRgcB572CW6Y3fB93L7BdFESr8IrzUQjbZwXsELZObCpD6Hlq87+P0DwtA0ryiZXOUs5uibe5ClphtSD4HAWJEWbHrWar6rNsq1PWle2z4H4P9QX4cuZX6+Y3yE8a4K1YAxiyeXcUQAUWFoZ1Wwewp4b/4iJCU9XyGIl4oMRKGie5y911wP2wgTTR3LvKjKzsjQmv6ysA4RqHbzCPt5DQDCffgHtix9bw0IPi1r/oG/HEYX1PRfFp4wnDBgtTE8ssxEUI169bKtg5G++r1lZ8EVXF3SJg8n0fyoCb2YcqGfFGj42YdC1Bj1V7LanMARxnmY7rXS1nYGsl6e7Xe5IOU99VWqNUgybYk3o0ddLGNSfdoxCAzZllYt1G0U8uz4JpBJlOiDjxDgZCMlboR0+Vsvh26bywCgvUSrhcgInM357Zs=; nguestv2=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJraWQiOiIzNDgyM2Q4YjIwZTY0NmFkYjI3MDJhYTYxZGZmZmU3NyIsImlhdCI6MTcxMjIxNTU1MCwiZXhwIjoxNzEyMjE1ODUwfQ.eHJWz_krMAHLvjjc2K4HPicn6AnVA0915XCUugIKDJc; nguestv2=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJraWQiOiI5YzJhMWZhMGRjNzU0YzdhODZjMjc2Zjg3ZDZmMmE1YyIsImlhdCI6MTcxMjIxNTU1MCwiZXhwIjoxNzEyMjE1ODUwfQ.YhBiuifJO-_hre9nPy8fm5SMV5kNvsmoFZ35DXgpKI8; __gads=ID=cf09f66d54094f68:T=1708083477:RT=1712215556:S=ALNI_MbhO83HKhGOCQQXQfdmmgjzm3Bogw; __gpi=UID=00000d23c624ba7a:T=1708083477:RT=1712215556:S=ALNI_MZAib_JwuvOsSphAgVFFx2j90A6TA; __eoi=ID=be755f0761063099:T=1708083477:RT=1712215556:S=AA-AfjbM-lVVgN8Os2C26-PAXtdi; _gat_UA-84507530-14=1; AKA_A2=A; _scid_r=066f7c4a-e8e7-464b-9391-07d9cf77d3ba; _uetsid=c57de2c0f1ba11ee8599cbb1529eb0d7; _uetvid=51c70f60cc9d11ee865e110d922a87f2; _clsk=xi50s1%7C1712215602267%7C22%7C0%7Ci.clarity.ms%2Fcollect; RT="z=1&dm=noon.com&si=cd4a450b-2adf-4ab3-9dd9-d834c2870f02&ss=lukuqliy&sl=g&tt=1hv6&obo=e&rl=1"; _etc=txe834bT7NewcK0A; bm_sv=4DEC2F57465F52E51024C8EEB5EA6DB7~YAAQHtYsF9xTMYqOAQAAQs0AqBfCgODjz+zWs7Cu37YMNHWzkZZfUjH14QGHe8n9URraxTg3cmzCE4sdllKH8AFhrROl/MCBJHtN+Mp5hW5lDhWqcWLzzQ9l6/shduYiLdv1Hc4OEnWGMcTGhRWpRdFovUmWZEF85V6yfGEhy3yaZWhgKiYYE0xuTzS22pq/bUU+v/k56L7dNe+cQOYAcQ+KH0ZxsIzAeVVnNLDSJt9IkeohHGPnwo5p/UMCR0p/~1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 100,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408],
        #'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter',
    }




    # categories = {
    #     #'Mobiles Tablets & Wearables
    #     'Electronics': {
    #         'Mobile Phones': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/mobiles-and-accessories/mobiles-20905/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #      #   'Mobile Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/mobiles-and-accessories/accessories-16176/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #      #   'Tablets & Ereaders': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/computers-and-accessories/tablets/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #       #  'Computers Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/computers-and-accessories/webcams/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
            
        
    #     },

    #     # 'Computers': {
    #     #     'Laptops': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/computers-and-accessories/laptops/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Software': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/software-10182/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Scanners': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/office-electronics/bar-code-scanners/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Scanners': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/office-electronics/scanner/?limit=50&originalQuery=Office%20Supplies&page={}&q=Office%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     # },

    #     # 'Video Games & Consoles': {
    #     #     'Games Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/video-games-10181/gaming-accessories/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Consoles': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/video-games-10181/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc'
    #     # },

    #     # 'Men & Women Watches': {
    #     #     'Watch Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/wearable-technology/smart-watches-and-accessories/smartwatch-accessories/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Unisex Watches': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/wearable-technology/smart-watches-and-accessories/smartwatches/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Women Watches': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/women-31229/womens-watches/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Men Watches': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/men-31225/mens-watches/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     "Women Watches": 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/girls-31223/girls-watches/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     "Men Watches": 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/boys-31221/boys-watches/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     # },

    #     #'Camcorders & Cameras
    #     'Electronics': {
    #         'Camera Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/accessories-16794/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         #'Security Cameras': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/surveillance-cameras-18886/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         'Camera Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/bags-and-cases-19385/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         #'Camcorders': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/video-17975/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         #'Digital Cameras': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/digital-cameras/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         'Camera Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/lenses-16166/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         #'Binoculars, Telescopes & Optics': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/binoculars-and-scopes/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         #'Digital Cameras': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/instant-cameras/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         #'Camcorders': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/camcorders/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         'Camera Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/flashes/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',    
    #     },

    #     #Video, Lcd & Oled
    #     'Electronics': {
    #         #'Video & Tv Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/television-and-video/television-accessories-16510/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         'Tv': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/television-and-video/televisions/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         #'Projectors & Screens': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/television-and-video/projectors/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         #'Projectors & Screens': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/television-and-video/projection-screens-20836/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         #'Home Theater': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/television-and-video/home-theater-systems-19095/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         #'Video & Tv Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/television-and-video/set-top-boxes-47527/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         #'Dvd, Blurays & Digital Media Players': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/television-and-video/streaming-media-players/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #         #'Dvd, Blurays & Digital Media Players': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/portable-audio-and-video/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     },

    #     # 'Audio, Headphones & Music Players': { 
    #     #     'Satellite Radios': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/television-and-video/satellite-equipments-accessories/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Home Audio': 'https://www.noon.com/_next/data/348a8bd34cca6abfd7639a39880e563d6e4d7391/uae-en/electronics-and-mobiles/home-audio.json?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc&catalog=electronics-and-mobiles&catalog=home-audio'
    #     #     },

    #     # 'Fashion': {
    #     #     'Women Clothes': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/women-31229/clothing-16021/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Women Shoes': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/women-31229/shoes-16238/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Women Jewellery': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/women-31229/womens-jewellery/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Women Jewellery': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/girls-31223/girls-jewellery/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Women Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/women-31229/accessories-16273/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Women Bags': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/women-31229/handbags-16699/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Men Clothes': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/men-31225/clothing-16204/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc', 
    #     #     'Men Shoes': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/men-31225/shoes-17421/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Men Jewellery': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/men-31225/mens-jewellery/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Men Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/men-31225/accessories-16205/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Men Bags': 'https://www.noon.com/_svc/catalog/api/v3/u/fashion/men-31225/handbags-and-shoulder-bags/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     # },

    #     # 'Baby & Kids': {
    #     #     'Girls Clothing': "https://www.noon.com/_svc/catalog/api/v3/u/fashion/girls-31223/clothing-16580/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Girls Shoes': "https://www.noon.com/_svc/catalog/api/v3/u/fashion/girls-31223/shoes-17594/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Girls Accessories': "https://www.noon.com/_svc/catalog/api/v3/u/fashion/girls-31223/accessories-17054/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Boys Clothing': "https://www.noon.com/_svc/catalog/api/v3/u/fashion/boys-31221/clothing-16097/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Boys Shoes': "https://www.noon.com/_svc/catalog/api/v3/u/fashion/boys-31221/shoes-16689/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Boys Accessories': "https://www.noon.com/_svc/catalog/api/v3/u/fashion/boys-31221/accessories-17386/?limit=50&originalQuery=Fashion&page={}&q=Fashion&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Feeding & Nursing': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/feeding-16153/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Diapers, Bath & Skincare': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/bathing-and-skin-care/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Nursery': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/nursery/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Diapers, Bath & Skincare': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/diapering/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Strollers, Gear & Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/baby-transport/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Safety Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/safety-17316/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Girls Clothing': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/clothing-shoes-and-accessories/baby-girls-16977/clothing-31217/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Girls Shoes': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/clothing-shoes-and-accessories/baby-girls-16977/shoes-27443/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Girls Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/clothing-shoes-and-accessories/baby-girls-16977/accessories-16978/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Boys Clothing': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/clothing-shoes-and-accessories/baby-boys-16213/clothing-31216/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Boys Shoes': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/clothing-shoes-and-accessories/baby-boys-16213/shoes-27430/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Boys Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/clothing-shoes-and-accessories/baby-boys-16213/accessories-20234/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc', 
    #     #     'Strollers, Gear & Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/baby-gear-accessories/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Baby Walkers': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/infant-activity/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Toys': 'https://www.noon.com/_svc/catalog/api/v3/u/toys-and-games/?limit=50&originalQuery=Toys%20and%20Games&page={}&q=Toys%20and%20Games&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc'
        
    #     # },

    #     # 'Groceries': {
    #     #     'Baby Food': 'https://www.noon.com/_svc/catalog/api/v3/u/baby-products/baby-food/?limit=50&originalQuery=Baby%20Products&page={}&q=Baby%20Products&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Pet Foods': 'https://www.noon.com/_svc/catalog/api/v3/u/pet-supplies/?limit=50&originalQuery=Pet%20Supplies&page={}&q=Pet%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     # },

    #     # 'Home Appliances': {
    #     #     'Kitchen Appliances': 'https://www.noon.com/_svc/catalog/api/v3/u/home-and-kitchen/kitchen-and-dining/?limit=50&originalQuery=Home%20and%20Kitchen&page={}&q=Home%20and%20Kitchen&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Home Appliances Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/home-and-kitchen/storage-and-organisation/?limit=50&originalQuery=Home%20and%20Kitchen&page={}&q=Home%20and%20Kitchen&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Home Appliances Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/home-and-kitchen/home-appliances-31235/?limit=50&originalQuery=Home%20and%20Kitchen&page={}&q=Home%20and%20Kitchen&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Home Appliances Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/home-and-kitchen/household-supplies/?limit=50&originalQuery=Home%20and%20Kitchen&page={}&q=Home%20and%20Kitchen&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Power Tools': 'https://www.noon.com/_svc/catalog/api/v3/u/tools-and-home-improvement/?limit=50&originalQuery=Tools%20and%20Home%20Improvement&page={}&q=Tools%20and%20Home%20Improvement&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     # },
        
    #     # 'Furniture, Home And Garden': {
    #     #     'Home Decor And Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/home-and-kitchen/home-decor/?limit=50&originalQuery=Home%20and%20Kitchen&page={}&q=Home%20and%20Kitchen&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Furniture': 'https://www.noon.com/_svc/catalog/api/v3/u/home-and-kitchen/furniture-10180/?limit=50&originalQuery=Home%20and%20Kitchen&page={}&q=Home%20and%20Kitchen&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Bathroom Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/home-and-kitchen/bath-16182/?limit=50&originalQuery=Home%20and%20Kitchen&page={}&q=Home%20and%20Kitchen&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Beds': 'https://www.noon.com/_svc/catalog/api/v3/u/home-and-kitchen/bedding-16171/?limit=50&originalQuery=Home%20and%20Kitchen&page={}&q=Home%20and%20Kitchen&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Outdoor': 'https://www.noon.com/_svc/catalog/api/v3/u/home-and-kitchen/patio-lawn-and-garden/?limit=50&originalQuery=Home%20and%20Kitchen&page={}&q=Home%20and%20Kitchen&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     # },

        
    #     # 'Personal Care & Beauty': {
    #     #     'Fragrances & Perfumes': "https://www.noon.com/_svc/catalog/api/v3/u/beauty/fragrance/?limit=50&originalQuery=Beauty%20and%20Fragrance&page={}&q=Beauty%20and%20Fragrance&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Personal Care For Women': "https://www.noon.com/_svc/catalog/api/v3/u/beauty/personal-care-16343/?f%5Bfragrance_department%5D%5B%5D=unisex&f%5Bfragrance_department%5D%5B%5D=women&limit=50&originalQuery=Beauty%20and%20Fragrance&page={}&q=Beauty%20and%20Fragrance&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Personal Care For Men': "https://www.noon.com/_svc/catalog/api/v3/u/beauty/personal-care-16343/?f%5Bfragrance_department%5D%5B%5D=unisex&f%5Bfragrance_department%5D%5B%5D=men&limit=50&originalQuery=Beauty%20and%20Fragrance&page={}&q=Beauty%20and%20Fragrance&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Personal Care For Women': "https://www.noon.com/_svc/catalog/api/v3/u/beauty/skin-care-16813/?limit=50&originalQuery=Beauty%20and%20Fragrance&page={}&q=Beauty%20and%20Fragrance&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Makeup & Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/beauty/makeup-16142/?limit=50&originalQuery=Beauty%20and%20Fragrance&page={}&q=Beauty%20and%20Fragrance&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Personal Care For Women': "https://www.noon.com/_svc/catalog/api/v3/u/beauty/hair-care/?limit=50&originalQuery=Beauty%20and%20Fragrance&page={}&q=Beauty%20and%20Fragrance&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Relaxation': "https://www.noon.com/_svc/catalog/api/v3/u/health/wellness/?limit=50&originalQuery=Health%20and%20Nutrition&page={}&q=Health%20and%20Nutrition&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Dental Care': 'https://www.noon.com/_svc/catalog/api/v3/u/health/dental-supplies/?limit=50&originalQuery=Health%20and%20Nutrition&page={}&q=Health%20and%20Nutrition&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc'
    #     # },

    #     # 'Books': {
    #     #     'Children Books': "https://www.noon.com/_svc/catalog/api/v3/u/books/childrens-books/?limit=50&originalQuery=Books&&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Fiction Books': "https://www.noon.com/_svc/catalog/api/v3/u/books/fiction-F/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Education & Reference Books': "https://www.noon.com/_svc/catalog/api/v3/u/books/reference-G/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Health, Mind & Body Books': "https://www.noon.com/_svc/catalog/api/v3/u/books/health-and-personal-development/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Photography & Art Books': "https://www.noon.com/_svc/catalog/api/v3/u/books/arts-architecture-and-photography/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     "Business & Investment Books": "https://www.noon.com/_svc/catalog/api/v3/u/books/business-and-finance/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     "Cooking & Food Books": "https://www.noon.com/_svc/catalog/api/v3/u/books/lifestyle-sport-and-leisure/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Cooking & Food Books': "https://www.noon.com/_svc/catalog/api/v3/u/books/food-drink/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Biography Books': 'https://www.noon.com/_svc/catalog/api/v3/u/books/biography-and-true-stories/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Biography Books': 'https://www.noon.com/_svc/catalog/api/v3/u/books/history-and-archaeology/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Languages & Dictionaries': "https://www.noon.com/_svc/catalog/api/v3/u/books/language/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Languages & Dictionaries': "https://www.noon.com/_svc/catalog/api/v3/u/books/english-language-teaching-(elt)/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Religion Books': "https://www.noon.com/_svc/catalog/api/v3/u/books/religious-and-spiritual/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Self Help Books': "https://www.noon.com/_svc/catalog/api/v3/u/books/society-and-social-sciences/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     "Science & Technology Books": "https://www.noon.com/_svc/catalog/api/v3/u/books/computer-and-technology/?limit=50&originalQuery=Books&page={}&q=Books&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc"
    #     # },


    #     # 'Health & Medical': {
    #     #     'Health And Fitness': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/exercise-and-fitness/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',

    #     # },

    #     # 'Sports Equipment': {
    #     #     'Watersports': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/boating-and-water-sports/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Rugby & Football': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/team-sports/football-17178/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Cricket': "https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/team-sports/cricket-16076/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Basketball': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/team-sports/basketball-17917/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Volleyball': "https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/team-sports/volleyball-16527/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc",
    #     #     'Baseball': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/team-sports/baseball-17952/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Basketball': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/team-sports/handball/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Mixed Martial Arts - MMA': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/combat-sports/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Badminton': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/racquet-sports-16542/badminton-19736/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Tennis': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/racquet-sports-16542/tennis-16543/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Table Tennis': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/racquet-sports-16542/table-tennis-18224/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Table Tennis': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/racquet-sports-16542/padel-tennis/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Squash': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/racquet-sports-16542/squash-21389/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Golf': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/precision-sports/golf-16322/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Darts': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/precision-sports/darts-and-dartboards/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Snooker & Pool': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/precision-sports/billiards/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Horse Riding': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports/equestrian-sports/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Cycling & Skating': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/cycling-16009/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Hiking & Outdoor': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/outdoor-recreation/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Sports Supplements': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports-nutrition-sports/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Fishing': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/hunting-and-fishing/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Cycling & Skating': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/action-sports/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Sports Bottles': 'https://www.noon.com/_svc/catalog/api/v3/u/sports-and-outdoors/sports-medicine/?limit=50&originalQuery=Sports%2C%20Fitness%20and%20Outdoors&page={}&q=Sports%2C%20Fitness%20and%20Outdoors&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Sports Supplements': 'https://www.noon.com/_svc/catalog/api/v3/u/health/sports-nutrition/?limit=50&originalQuery=Health%20and%20Nutrition&page={}&q=Health%20and%20Nutrition&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        
    #     # },

    #     # 'Office Supplies': {
    #     #     'Stationary': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/writing-and-correction-supplies-16515/?limit=50&originalQuery=Office%20Supplies&page={}&q=Office%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Stationary': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/stationery-16397/?limit=50&originalQuery=Office%20Supplies&page={}&q=Office%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Id Card Printer & Supplies': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/office-electronics/printer-accessories-18895/?limit=50&originalQuery=Office%20Supplies&page={}&q=Office%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Id Card Printer & Supplies': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/office-electronics/stationery-printers/?limit=50&originalQuery=Office%20Supplies&page={}&q=Office%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Interactive Whiteboards': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/office-electronics/presentation-products/?limit=50&originalQuery=Office%20Supplies&page={}&q=Office%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Shredders': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/office-electronics/shredders/?limit=50&originalQuery=Office%20Supplies&page={}&q=Office%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Calculators': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/office-electronics/calculators/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Laminators': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/office-electronics/laminators/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Stationary': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/gift-wrapping-supplies/?limit=50&originalQuery=Office%20Supplies&page={}&q=Office%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Label & Barcode Printers': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/office-electronics/label-makers-24710/?limit=50&originalQuery=Office%20Supplies&page={}&q=Office%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Point Of Sale': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/office-electronics/cash-registers-18518/?limit=50&originalQuery=Office%20Supplies&page={}&q=Office%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Desk-Phones': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/office-electronics/telephones-and-accessories/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Paper Products': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/paper-16454/?limit=50&originalQuery=Office%20Supplies&page={}&q=Office%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Stationary': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/envelopes-mailers-and-shipping-supplies/?limit=50&originalQuery=Office%20Supplies&page={}&q=Office%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Time Recorder, Cards & Racks': 'https://www.noon.com/_svc/catalog/api/v3/u/office-supplies/time-clocks-and-cards/?limit=50&originalQuery=Office%20Supplies&page={}&q=Office%20Supplies&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',

    #     # },

    #     # 'Health & Medical': {
    #     #     'Vitamins & Herbals': 'https://www.noon.com/_svc/catalog/api/v3/u/health/vitamins-and-dietary-supplements/?limit=50&originalQuery=Health%20and%20Nutrition&page={}&q=Health%20and%20Nutrition&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Appliances': 'https://www.noon.com/_svc/catalog/api/v3/u/health/medical-supplies-and-equipment/?limit=50&originalQuery=Health%20and%20Nutrition&page={}&q=Health%20and%20Nutrition&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Medicine': 'https://www.noon.com/_svc/catalog/api/v3/u/health/health-care/?limit=50&originalQuery=Health%20and%20Nutrition&page={}&q=Health%20and%20Nutrition&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Nutrition': 'https://www.noon.com/_svc/catalog/api/v3/u/health/nutrition-and-wellness/?limit=50&originalQuery=Health%20and%20Nutrition&page={}&q=Health%20and%20Nutrition&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Cold, Cough & Flu': 'https://www.noon.com/_svc/catalog/api/v3/u/health/cough-cold-and-flu/?limit=50&originalQuery=Health%20and%20Nutrition&page={}&q=Health%20and%20Nutrition&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Sexual Wellness': 'https://www.noon.com/_svc/catalog/api/v3/u/health/sexual-wellness/?limit=50&originalQuery=Health%20and%20Nutrition&page={}&q=Health%20and%20Nutrition&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc'
    #     # },

    #     # 'Car Parts & Accessories': {
    #     #     'Interior Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/automotive/interior-accessories/?limit=50&originalQuery=Automotive&page={}&q=Automotive&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Exterior Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/automotive/exterior-accessories/?limit=50&originalQuery=Automotive&page={}&q=Automotive&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Car Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/automotive/replacement-parts-16014/?limit=50&originalQuery=Automotive&page={}&q=Automotive&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Interior Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/automotive/car-care/interior-care/?limit=50&originalQuery=Automotive&page={}&q=Automotive&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Exterior Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/automotive/car-care/exterior-care/?limit=50&originalQuery=Automotive&page={}&q=Automotive&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Car Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/automotive/car-body-parts/?limit=50&originalQuery=Automotive&page={}&q=Automotive&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Car Video': 'https://www.noon.com/_svc/catalog/api/v3/u/automotive/car-and-vehicle-electronics/car-electronics-16079/car-video/?limit=50&originalQuery=Automotive&page={}&q=Automotive&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Car Audio': 'https://www.noon.com/_svc/catalog/api/v3/u/automotive/car-and-vehicle-electronics/car-electronics-16079/car-audio/?limit=50&originalQuery=Automotive&page={}&q=Automotive&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Car Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/automotive/tires-and-wheels-16878/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Car Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/automotive/oils-and-fluids/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Car Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/automotive/rv-parts-and-accessories/?limit=50&page={}&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     # },

    #     # 'Musical Instruments': {
    #     #     'Guitar Instruments': 'https://www.noon.com/_svc/catalog/api/v3/u/music-movies-and-tv-shows/musical-instruments-24670/guitars/?limit=50&originalQuery=Musical%20Instruments&page={}&q=Musical%20Instruments&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Drums & Percussions Instruments': 'https://www.noon.com/_svc/catalog/api/v3/u/music-movies-and-tv-shows/musical-instruments-24670/percussion-music/?limit=50&originalQuery=Musical%20Instruments&page={}&q=Musical%20Instruments&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Keyboards & Midi Instruments': 'https://www.noon.com/_svc/catalog/api/v3/u/music-movies-and-tv-shows/musical-instruments-24670/pianos-keyboards-synthesizers/?limit=50&originalQuery=Musical%20Instruments&page={}&q=Musical%20Instruments&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     #     'Orchestral Strings Instruments': 'https://www.noon.com/_svc/catalog/api/v3/u/music-movies-and-tv-shows/musical-instruments-24670/stringed-instruments/?limit=50&originalQuery=Musical%20Instruments&page={}&q=Musical%20Instruments&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
    #     # },
    # }

    categories = {
  

        'Electronics': {
            #'Mobile Phones': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/mobiles-and-accessories/mobiles-20905/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
            'Tv': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/television-and-video/televisions/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
            # 'Camera Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/accessories-16794/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
            # 'Camera Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/bags-and-cases-19385/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
            # 'Camera Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/lenses-16166/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
            # 'Camera Accessories': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/camera-and-photo-16165/flashes/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',    
            'Laptops': 'https://www.noon.com/_svc/catalog/api/v3/u/electronics-and-mobiles/computers-and-accessories/laptops/?limit=50&originalQuery=electronics&page={}&q=electronics&searchDebug=false&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc',
        },

    }

    page = 0
    count = 0

    conn = psycopg2.connect(
        dbname="retailifydb3",
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    def __init__(self, reviews='False', short_scraper="False", *args, **kwargs):
        super().__init__()

         # Set up the log directory and file path
        log_dir = 'scrapy-logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)  # Create the directory if it doesn't exist

        log_file = f'{log_dir}/{self.name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log'
        self.custom_settings['LOG_FILE'] = log_file

        self.reviews = reviews.lower() == 'true'
        self.short_scraper = short_scraper.lower() == 'true'
        catalogue_url = CATALOGUE_URL_T.format(self.name, self.short_scraper)
        categories_url = "{}{}".format(HOST, catalogue_url)
        raw_res = requests.get(categories_url).json()
    #     self.categories = raw_res.get('data', [])
        self.vendor_code = raw_res.get('VendorCode')

    def get_catalogue_code(self, catalogue_name):
        # Attempt to retrieve the catalog code and name from the database
        query_select = 'SELECT "CatalogueCode", "CatalogueName" FROM product_catalogue WHERE "CatalogueName" = %s'
        self.cursor.execute(query_select, (catalogue_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the catalog code exists, check if the name needs to be updated
            if result[1] != catalogue_name:
                update_query = 'UPDATE product_catalogue SET "CatalogueName" = %s WHERE "CatalogueCode" = %s'
                self.cursor.execute(update_query, (catalogue_name, result[0]))
                self.conn.commit()  # Commit the transaction
                
            return result[0]
        else:
            # If the catalog code doesn't exist, insert it into the database
            insert_query = 'INSERT INTO product_catalogue ("CatalogueName") VALUES (%s) RETURNING "CatalogueCode"'
            self.cursor.execute(insert_query, (catalogue_name,))
            self.conn.commit()  # Commit the transaction

            # # Retrieve the newly inserted category code and name
            # self.cursor.execute(query_select, (catalogue_name,))
            # result = self.cursor.fetchone()
            # return result[0] if result else None
        
            result = self.cursor.fetchone()
            return result[0] if result else None


    
    def get_category_code(self, category_name, catalogue_code):
        # Attempt to retrieve the category code and name from the database
        query_select = 'SELECT "CategoryCode", "CategoryName" FROM product_category WHERE "CategoryName" = %s'
        self.cursor.execute(query_select, (category_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the category code exists, check if the name needs to be updated
            if result[1] != category_name:
                update_query = 'UPDATE product_category SET "CategoryName" = %s WHERE "CategoryCode" = %s'
                self.cursor.execute(update_query, (category_name, result[0]))
                self.conn.commit()  # Commit the transaction
            
            return result[0]
        else:
            # If the category code doesn't exist, insert it into the database
            insert_query = 'INSERT INTO product_category ("CategoryName", "CatalogueCode_id") VALUES (%s, %s) RETURNING "CategoryCode"'
            self.cursor.execute(insert_query, (category_name, catalogue_code))
            self.conn.commit()  # Commit the transaction
            
            # # Retrieve the newly inserted category code and name
            # self.cursor.execute(query_select, (category_name,))
            # result = self.cursor.fetchone()
            # return result[0] if result else None
            result = self.cursor.fetchone()
            return result[0] if result else None
    
    def start_requests(self):
        for main_category, sub_categories in self.categories.items():
            for sub_category, cat_url in sub_categories.items():
                catalogue_code = self.get_catalogue_code(main_category)  # Assuming you have this method implemented
                if catalogue_code:
                    yield scrapy.Request(url=cat_url.format(self.page), headers=self.headers, meta={'category': main_category, 'sub_category': sub_category, 'cat_url': cat_url, 'page': self.page, 'catalogue_code': catalogue_code})

    def parse(self, response):
        data = json.loads(response.text)
        page = response.meta['page']
        cat_url = response.meta['cat_url']
        vendor_code = self.vendor_code
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        #sub_category = data.get('analytics',{}).get('ed', {}).get('pcat', [])
        # if sub_category:
        #     item['CategoryName'] = sub_category[0]
        hits = data.get("hits", [])
        if hits:
            for hit in hits:
                item = ProductItemNoon()
                item['SKU'] = hit.get('sku')
                item['BrandName'] = hit.get('brand')
                item['ProductName'] = hit.get('name')
                item['CatalogueName'] = category
                item['CategoryName'] = sub_category
                item['ProductName'] = item['ProductName'].strip()
                item['RegularPrice'] = hit.get('price')
                item['RegularPrice'] = round(float(item['RegularPrice']), 2)
                item['Offer'] = hit.get('sale_price')
                if not item['Offer']:
                    item['Offer'] = 0
                item['Offer'] = round(float(item['Offer']), 2)
                item['StockAvailability'] = hit.get('is_buyable')
                item['RatingValue'] = hit.get('product_rating', {}).get('value', 0)
                item['RatingValue'] = round(float(item['RatingValue']), 2)
                url = hit.get('url')
                item['URL'] = self.url_product_template.format(url, item['SKU'])
                img = hit.get('image_key')
                item['MainImage'] = self.img_product_template.format(img)
                item['ModelNumber'] = hit.get('plp_specifications', {}).get('Model Number')
                if not item['ModelNumber']:
                    item['ModelNumber'] = ''

                item['VendorCode'] = vendor_code
                item['BrandCode'] = ''
                item['Currency'] = 'AED'
                item['Market'] = 'UAE'
                #item['About'] = ''
                catalogue_code = response.meta['catalogue_code']
                category_code = self.get_category_code(item['CategoryName'], catalogue_code)
                item['CatalogueCode'] = catalogue_code
                item['CategoryCode'] = category_code

                # yield item
                #updated_body = {k: v.format(item['SKU']) if isinstance(v, str) else v for k, v in self.body.items()}
                #yield scrapy.Request(url=self.review_url, headers=self.review_headers, method='POST', body=json.dumps(updated_body), callback=self.parse_review, meta={'item': item})
                yield scrapy.Request(url=item['URL'], headers=self.headers, callback=self.parse_description, meta={'item': deepcopy(item)})

            #NEXT PAGE
            page = page + 1
            yield scrapy.Request(url=cat_url.format(page), headers=self.headers, meta={'category': category, 'sub_category': sub_category, 'cat_url': cat_url, 'page': page, 'catalogue_code': catalogue_code})


    def parse_description(self, response):
        item = response.meta['item']
        
        # Extract the 'About' section
        about_list = response.xpath('//div[@class="sc-97eb4126-2 oPZpQ"]/ul/li/text()').getall()
        about = "\n".join(about_list)
        item['About'] = about

        # Extract model number if missing
        if not item["ModelNumber"]:
            model_number = response.xpath('//td[text()="Model Number"]/following-sibling::td[1]/text()').get()
            item['ModelNumber'] = model_number if model_number else ''

        # Extract additional dynamic attributes
        color = response.xpath('//td[text()="Colour Name"]/following-sibling::td[1]/text()').get()
        internal_memory = response.xpath('//td[text()="Internal Memory"]/following-sibling::td[1]/text()').get()
        os_version = response.xpath('//td[text()="Operating System Number"]/following-sibling::td[1]/text()').get()
        processor_number = response.xpath('//td[text()="Processor Number"]/following-sibling::td[1]/text()').get()
        ram = response.xpath('//td[text()="RAM Size"]/following-sibling::td[1]/text()').get()

        # Store attributes dynamically
        dynamic_attributes = []
        
        if color:
            dynamic_attributes.append({'name': 'Color', 'value': color.strip()})

        if internal_memory:
            dynamic_attributes.append({'name': 'Internal Memory', 'value': internal_memory.strip()})

        if os_version:
            dynamic_attributes.append({'name': 'OS Version', 'value': os_version.strip()})

        if processor_number:
            dynamic_attributes.append({'name': 'Processor Number', 'value': processor_number.strip()})

        if ram:
            dynamic_attributes.append({'name': 'RAM', 'value': ram.strip()})

        # Add the dynamic attributes to the item
        item['attributes'] = dynamic_attributes

        # Yield the final item
        yield item


    # def parse_review(self, response):
    #     item = response.meta['item']
    #     data = json.loads(response.text)
    #     item_reviews = []
    #     list = data.get('list', [])
    #     if list:
    #         for review in list:
    #             comment = review.get('comment', '')
    #             source = ''
    #             comment_date = review.get('updatedAt', '')
    #             rating = round(float(review.get('rating')), 2)
    #             max_rating = round(5, 2)
                
    #             review_data = {
    #                 'Comment': comment,
    #                 'Source': source,
    #                 'CommentDate': comment_date,
    #                 'rating': rating,
    #                 'max_rating': max_rating,
    #                 'average_rating': rating
    #             }
    #             item_reviews.append(review_data)
    #         item['reviews'] = item_reviews

    #     else:
    #         pass

    #     yield item
     





