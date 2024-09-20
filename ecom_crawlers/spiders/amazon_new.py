import re
import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemAmazon
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import psycopg2
import os 

class AmazonSpider(Spider):
    name = 'amazon'
    allowed_domains = ['www.amazon.ae']
    main_url = 'https://www.amazon.ae'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.amazon.com/',
        'Connection': 'keep-alive',
    }

    cat_products_urls = {

                'Mobiles Tablets & Wearable': {
                    'Mobile Phones': 'https://www.amazon.ae/s?rh=n%3A12303750031&fs=true&ref=lp_12303750031_sar',
                    #'Mobile Accessories': 'https://www.amazon.ae/s?rh=n%3A12303803031&fs=true&ref=lp_12303803031_sar',
                    #'Tablets & Ereaders': 'https://www.amazon.ae/gp/browse.html?node=12050253031&ref_=nav_em_mob_tablets_0_2_5_3',
                    #'Wearables': 'https://www.amazon.ae/s?rh=n%3A12303756031&fs=true&ref=lp_12303756031_sar',
                    #'Mobile Accessories': 'https://www.amazon.ae/s?rh=n%3A15415115031&fs=true&ref=lp_15415115031_sar',
                    #'Mobile Accessories': 'https://www.amazon.ae/gp/browse.html?node=12304344031&ref_=nav_em_mob_power_banks_0_2_5_6',
                },
                
                'Computers': {
                    'Laptops': "https://www.amazon.ae/s?rh=n%3A12050245031&fs=true&ref=lp_12050245031_sar",
                    'Desktop': "https://www.amazon.ae/s?bbn=15387140031&rh=n%3A11497745031%2Cn%3A15387140031%2Cn%3A12050242031&dc&qid=1714144497&rnid=11497746031&ref=lp_15387140031_nr_n_4",
                    #'Monitors': 'https://www.amazon.ae/s?bbn=15387140031&rh=n%3A11497745031%2Cn%3A15387140031%2Cn%3A12050246031&dc&qid=1714144497&rnid=11497746031&ref=lp_15387140031_nr_n_6',
                    #'Hard Drives & Storage': 'https://www.amazon.ae/s?rh=n%3A12050241031&fs=true&ref=lp_12050241031_sar',
                   # 'Networking & Wireless': 'https://www.amazon.ae/gp/browse.html?node=12050247031&ref_=nav_em_pc_networking_0_2_6_6',
                    #'Mouse, Keyboards & Input': 'https://www.amazon.ae/gp/browse.html?node=12050260031&ref_=nav_em_pc_key_mouse_0_2_6_7',
                    'Desktop': 'https://www.amazon.ae/s?bbn=15387140031&rh=n%3A11497745031%2Cn%3A15387140031%2Cn%3A12050242031&dc&qid=1714378967&rnid=11497746031&ref=lp_15387140031_nr_n_4',
                    #'Computer Parts': 'https://www.amazon.ae/s?rh=n%3A26955028031&fs=true&ref=lp_26955028031_sar',
                    #'Computers Accessories': 'https://www.amazon.ae/s?rh=n%3A12050239031&fs=true&ref=lp_12050239031_sar',
                    #'Printers & Ink': 'https://www.amazon.ae/s?rh=n%3A12050248031&fs=true&ref=lp_12050248031_sar',  
                },

                # 'Arts & Crafts': {
                #     'Art Tools And Accessories': 'https://www.amazon.ae/b?node=15172571031&ref=lp_15150351031_nr_n_0',
                # },

                # 'Furniture, Home And Garden': {
                #     'Furniture': 'https://www.amazon.ae/b?node=15172574031&ref=lp_15150351031_nr_n_3',
                #     'Home Decor And Accessories': 'https://www.amazon.ae/s?rh=n%3A12148101031&fs=true&ref=lp_12148101031_sar',
                #     'Furniture': 'https://www.amazon.ae/s?rh=n%3A12148100031&fs=true&ref=lp_12148100031_sar',
                #     'Bathroom Accessories': 'https://www.amazon.ae/s?rh=n%3A11497916031&fs=true&ref=lp_11497916031_sar',
                #     'Outdoor': 'https://www.amazon.ae/s?rh=n%3A15149894031&fs=true&ref=lp_15149894031_sar',

                # },

                # 'Office Supplies': {
                #     'Paper Products': 'https://www.amazon.ae/b?node=15172576031&ref=lp_15150351031_nr_n_5',
                #     'Stationary': 'https://www.amazon.ae/b?node=15172578031&ref=lp_15150351031_nr_n_7',
                #     'Stationary': 'https://www.amazon.ae/b?node=15172579031&ref=lp_15150351031_nr_n_8',
                #     'Stationary': 'https://www.amazon.ae/gp/browse.html?node=11996021031&ref_=nav_em_sl_k_bags_0_2_10_8',
                #     'Paper Products': 'https://www.amazon.ae/s?rh=n%3A21246379031&fs=true&ref=lp_21246379031_sar',
                # },

                'Video, Lcd & Oled': {
                    'Tv': 'https://www.amazon.ae/s?rh=n%3A12303800031&fs=true&ref=lp_12303800031_sar',
                    #'Home Theater': 'https://www.amazon.ae/gp/browse.html?node=12303794031&ref_=nav_em_elec_audio_video_0_2_7_6'
                },
                
                'Camcorders & Cameras': {
                    'Digital Cameras': 'https://www.amazon.ae/s?rh=n%3A12303745031&fs=true&ref=lp_12303745031_sar',

                },

                # 'Video Games & Consoles': {
                #     'Consoles': 'https://www.amazon.ae/s?rh=n%3A11601383031&fs=true&ref=lp_11601383031_sar',

                # },

                'Audio, Headphones & Music Players': {
                    'Headphones & Speakers': 'https://www.amazon.ae/s?rh=n%3A12303875031&fs=true&ref=lp_12303875031_sar',
                    'Headphones & Speakers': 'https://www.amazon.ae/s?rh=n%3A12303788031&fs=true&ref=lp_12303788031_sar',
                },

                # 'Musical Instruments': {
                #     'Amplifiers & Effects Instruments': 'https://www.amazon.ae/b?node=15176028031&ref=lp_15150237031_nr_n_0',
                #     'Guitar Instruments': 'https://www.amazon.ae/s?rh=n%3A15176029031&fs=true&ref=lp_15176029031_sar',
                #     'Drums & Percussions Instruments': 'https://www.amazon.ae/s?rh=n%3A15176031031&fs=true&ref=lp_15176031031_sar',
                #     'Guitar Instruments': 'https://www.amazon.ae/b?node=15176033031&ref=lp_15150237031_nr_n_5',
                #     'Guitar Instruments': 'https://www.amazon.ae/s?rh=n%3A27009013031&fs=true&ref=lp_27009013031_sar',
                #     'Keyboards & Midi Instruments': 'https://www.amazon.ae/b?node=15176037031&ref=lp_15150237031_nr_n_10',
                #     'Orchestral Strings Instruments': 'https://www.amazon.ae/s?rh=n%3A15176039031&fs=true&ref=lp_15176039031_sar',
                #     'Folk & Woodwind Instruments': 'https://www.amazon.ae/s?rh=n%3A15176041031&fs=true&ref=lp_15176041031_sar',
                # },

                # 'Home Appliances': {
                #     'Kitchen Appliances': 'https://www.amazon.ae/s?rh=n%3A16566535031&fs=true&ref=lp_16566535031_sar',
                #     'Home Necessities': 'https://www.amazon.ae/s?rh=n%3A16450420031&fs=true&ref=lp_16450420031_sar',
                #     'Kitchen Appliances': 'https://www.amazon.ae/gp/browse.html?node=15298040031&ref_=nav_em_appl_coffee_0_2_7_15',
                #     'Kitchen Appliances': 'https://www.amazon.ae/s?rh=n%3A16400439031&fs=true&ref=lp_16400439031_sar',
                #     'Vacuum Cleaners': 'https://www.amazon.ae/gp/browse.html?node=12134247031&ref_=nav_em_appl_vacuums_0_2_7_17',
                #     'Kitchen Appliances': 'https://www.amazon.ae/gp/browse.html?node=15174961031&ref_=nav_em_appl_refrigerators_0_2_7_18',
                #     'Washers & Dryers': 'https://www.amazon.ae/gp/browse.html?node=15174965031&ref_=nav_em_appl_washing_machine_0_2_7_19',
                #     'Washers & Dryers': 'https://www.amazon.ae/s?rh=n%3A15160105031&fs=true&ref=lp_15160105031_sar',
                #     'Washers & Dryers': 'https://www.amazon.ae/s?rh=n%3A21098590031&fs=true&ref=lp_21098590031_sar',
                #     'Home Appliances Accessories': 'https://www.amazon.ae/s?rh=n%3A11601269031&fs=true&ref=lp_11601269031_sar',
                #     'Lighting': 'https://www.amazon.ae/s?rh=n%3A16566537031&fs=true&ref=lp_16566537031_sar',
                #     'Home Appliances Accessories': 'https://www.amazon.ae/s?rh=n%3A12148103031&fs=true&ref=lp_12148103031_sar',
                #     'Kitchen Appliances': 'https://www.amazon.ae/s?rh=n%3A16402718031&fs=true&ref=lp_16402718031_sar',
                #     #'Home Appliances Accessories': '',

                # },

                # 'Fashion': {
                #     'Women Clothing': 'https://www.amazon.ae/s?k=women+clothing&rh=n%3A11995873031&ref=nb_sb_noss',
                #     'Women Jewellery': 'https://www.amazon.ae/s?rh=n%3A11995892031&fs=true&ref=lp_11995892031_sar',
                #     'Women Sportswear': 'https://www.amazon.ae/s?rh=n%3A11996189031&fs=true&ref=lp_11996189031_sar',
                #     'Women Clothing': 'https://www.amazon.ae/s?rh=n%3A11996199031&fs=true&ref=lp_11996199031_sar',
                #     'Women Clothing': 'https://www.amazon.ae/s?bbn=21648677031&rh=n%3A11497631031%2Cn%3A%2111497636031%2Cn%3A%2111497638031%2Cn%3A%2121611470031%2Cn%3A%2121611471031%2Cn%3A%2121648675031%2Cn%3A%2121648676031%2Cn%3A21648677031%2Cn%3A11995849031&dc&fst=as%3Aoff&qid=1611475788&rnid=11497632031&ref=nav_em_sl_w_outlet_0_2_8_7',
                #     'Women Shoes': 'https://www.amazon.ae/s?rh=n%3A11995893031&fs=true&ref=lp_11995893031_sar',
                #     'Women Bags': 'https://www.amazon.ae/gp/browse.html?node=11995843031&ref_=nav_em_sl_luggage_back_0_2_8_10',
                #     'Women Bags': 'https://www.amazon.ae/gp/browse.html?node=11995891031&ref_=nav_em_sl_w_bags_wallets_0_2_8_11',
                #     'Women Accessories': 'https://www.amazon.ae/s?rh=n%3A11996178031&fs=true&ref=lp_11996178031_sar',
                #     'Women Shoes': 'https://www.amazon.ae/gp/browse.html?node=11996234031&ref_=nav_em_sl_w_shoes_spt_0_2_8_13',
                #     'Women Perfumes': 'https://www.amazon.ae/gp/browse.html?node=12149502031&ref_=nav_em_perfume_women_0_2_11_10',

                #     'Men Clothing': 'https://www.amazon.ae/s?k=men+clothing&rh=n%3A11995873031&ref=nb_sb_noss',
                #     'Men Sportswear': 'https://www.amazon.ae/s?rh=n%3A11996059031&fs=true&ref=lp_11996059031_sar',
                #     'Men Accessories': 'https://www.amazon.ae/gp/browse.html?node=11995872031&ref_=nav_em_sl_m_accessories_0_2_9_5',
                #     'Men Clothing': 'https://www.amazon.ae/gp/browse.html?node=11996075031&ref_=nav_em_sl_m_underwear_0_2_9_6',
                #     'Men Clothing': 'https://www.amazon.ae/s?bbn=21648677031&rh=n%3A11497631031%2Cn%3A%2111497636031%2Cn%3A%2111497638031%2Cn%3A%2121611470031%2Cn%3A%2121611471031%2Cn%3A%2121648675031%2Cn%3A%2121648676031%2Cn%3A21648677031%2Cn%3A11995844031&dc&fst=as%3Aoff&qid=1611475788&rnid=11497632031&ref=nav_em_sl_m_outlet_0_2_9_7',
                #     'Men Shoes': 'https://www.amazon.ae/s?rh=n%3A11995876031&fs=true&ref=lp_11995876031_sar',
                #     'Men Bags': 'https://www.amazon.ae/gp/browse.html?node=11995874031&ref_=nav_em_sl_m_bags_wallets_0_2_9_10',
                #     'Men Accessories': 'https://www.amazon.ae/s?rh=n%3A11996046031&fs=true&ref=lp_11996046031_sar',
                #     'Men Bags': 'https://www.amazon.ae/gp/browse.html?node=11995843031&ref_=nav_em_sl_luggage_back_0_2_9_12',
                #     'Men Shoes': 'https://www.amazon.ae/s?rh=n%3A11996088031&fs=true&ref=lp_11996088031_sar',
                #     'Men Perfumes': 'https://www.amazon.ae/gp/browse.html?node=12149499031&ref_=nav_em_perfume_men_0_2_11_9',

                # },

                # 'Men & Women Watches': {
                #     'Women Watches': 'https://www.amazon.ae/s?rh=n%3A11995894031&fs=true&ref=lp_11995894031_sar',
                #     'Men Watches': 'https://www.amazon.ae/s?rh=n%3A11995877031&fs=true&ref=lp_11995877031_sar',
                # },

                # 'Personal Care & Beauty': {
                #     'Makeup & Accessories': 'https://www.amazon.ae/s?rh=n%3A11497859031&fs=true&ref=lp_11497859031_sar',
                #     'Dental Care': 'https://www.amazon.ae/gp/browse.html?node=12373018031&ref_=nav_em_hpc_dental_care_0_2_11_17',
                #     'Makeup & Accessories': 'https://www.amazon.ae/s?i=specialty-aps&srs=16630973031&rh=n%3A16630973031&fs=true&ref=lp_16630973031_sar',
                # },

                # 'Groceries': {
                #     'Nutrition': 'https://www.amazon.ae/s?rh=n%3A12373019031&fs=true&ref=lp_12373019031_sar',
                #     'Food Cupboard': 'https://www.amazon.ae/s?rh=n%3A15387142031&fs=true&ref=lp_15387142031_sar',
                #     'Drinks': 'https://www.amazon.ae/s?rh=n%3A15159985031&fs=true&ref=lp_15159985031_sar',
                #     'Crisps, Snacks & Nuts': 'https://www.amazon.ae/s?rh=n%3A15160005031&fs=true&ref=lp_15160005031_sar',
                #     'Cooking Ingredients': 'https://www.amazon.ae/s?rh=n%3A15387143031&fs=true&ref=lp_15387143031_sar',
                #     'Pet Foods': 'https://www.amazon.ae/s?rh=n%3A15150407031&fs=true&ref=lp_15150407031_sar',

                # },

                # 'Baby & Kids': {
                #     'Boys Clothing': 'https://www.amazon.ae/gp/browse.html?node=11995853031&ref_=nav_em_sl_b_clothing_0_2_10_2',
                #     'Girls Clothing': 'https://www.amazon.ae/gp/browse.html?node=11995859031&ref_=nav_em_sl_g_clothing_0_2_10_3',
                #     'Boys Accessories': 'https://www.amazon.ae/s?bbn=21720575031&rh=n%3A11497631031%2Cn%3A21720575031%2Cn%3A11995841031&dc&qid=1714380211&rnid=11497632031&ref=lp_21720575031_nr_n_2',
                #     'Girls Accessories': 'https://www.amazon.ae/s?bbn=21720575031&rh=n%3A11497631031%2Cn%3A21720575031%2Cn%3A11995842031&dc&qid=1714380211&rnid=11497632031&ref=lp_21720575031_nr_n_1',
                #     'Boys Shoes': 'https://www.amazon.ae/gp/browse.html?node=11995856031&ref_=nav_em_sl_b_shoes_0_2_10_6',
                #     'Girls Shoes': 'https://www.amazon.ae/gp/browse.html?node=11995862031&ref_=nav_em_sl_g_shoes_0_2_10_7',
                #     'Diapers, Bath & Skincare': 'https://www.amazon.ae/s?rh=n%3A12198694031&fs=true&ref=lp_12198694031_sar',
                #     'Strollers, Gear & Accessories': 'https://www.amazon.ae/gp/browse.html?node=12198769031&ref_=nav_em_baby_strollers_0_2_15_5',
                #     'Feeding & Nursing': 'https://www.amazon.ae/gp/browse.html?node=12198697031&ref_=nav_em_baby_nursing_feeding_0_2_15_6',
                #     'Toys': 'https://www.amazon.ae/s?rh=n%3A17930529031&fs=true&ref=lp_17930529031_sar',
                # },

                # 'Health & Medical': {
                #     'Health And Fitness': 'https://www.amazon.ae/s?rh=n%3A11601212031&fs=true&ref=lp_11601212031_sar',
                # },

                # 'Books': {
                #     'Arabic Books': 'https://www.amazon.ae/s?bbn=11497688031&rh=n%3A11497688031%2Cp_n_feature_nine_browse-bin%3A15412915031&ref=nav_em_bks_arabic_0_2_17_3',
                #     'Children Books': 'https://www.amazon.ae/s?rh=n%3A12379684031&fs=true&ref=lp_12379684031_sar',
                #     'Business & Investment Books': 'https://www.amazon.ae/s?rh=n%3A12379682031&fs=true&ref=lp_12379682031_sar',
                #     'Self Help Books': 'https://www.amazon.ae/s?rh=n%3A12379874031&fs=true&ref=lp_12379874031_sar',
                #     'Cooking & Food Books': 'https://www.amazon.ae/s?rh=n%3A12379687031&fs=true&ref=lp_12379687031_sar',
                #     'Fiction Books': 'https://www.amazon.ae/s?rh=n%3A12379699031&fs=true&ref=lp_12379699031_sar',
                #     'Biography Books': 'https://www.amazon.ae/s?rh=n%3A12379681031&fs=true&ref=lp_12379681031_sar',
                # },

                # 'Video Games & Consoles': {
                #     'Playstation 5 Games': 'https://www.amazon.ae/s?rh=n%3A20904689031&language=en_AE&brr=1&rd=1&ref=nav_em_vg_playstation5_0_2_18_3',
                #     'Xbox 360 Games': 'https://www.amazon.ae/s?rh=n%3A20904706031&language=en_AE&brr=1&rd=1&ref=nav_em_vg_xbox_x_0_2_18_4',
                #     'Playstation 4 Games': 'https://www.amazon.ae/s?rh=n%3A12359187031&fs=true&ref=lp_12359187031_sar',
                #     'Xbox One Games': 'https://www.amazon.ae/gp/browse.html?node=12359193031&ref_=nav_em_vg_xbox_one_0_2_18_6',
                #     'Nintendo Switch Games': 'https://www.amazon.ae/s?rh=n%3A12359183031&fs=true&ref=lp_12359183031_sar',
                #     'Video Games & Keys': 'https://www.amazon.ae/s?rh=n%3A89266298031&fs=true&ref=lp_89266298031_sar',
                #     'Video Games & Keys': 'https://www.amazon.ae/s?rh=n%3A12359184031&fs=true&ref=lp_12359184031_sar',
                #     'Games Accessories': 'https://www.amazon.ae/s?rh=n%3A15387145031&fs=true&ref=lp_15387145031_sar',
                # },

                # 'Car Parts & Accessories': {
                #     'Car Accessories': 'https://www.amazon.ae/s?rh=n%3A11498030031&fs=true&ref=lp_11498030031_sar',
                # },
 
        }

    # custom_settings = {
    #     'DOWNLOAD_DELAY': 0.5,
    #     'RETRY_TIMES': 3,
    #     'DOWNLOAD_TIMEOUT': 200,
    #     'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
    #     #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    # }

    custom_settings = {
        'DOWNLOAD_DELAY': 2.0,  # Adjusted download delay to 2 seconds
        'RETRY_TIMES': 10,      # Increased retry times to 10
        'DOWNLOAD_TIMEOUT': 100,  # Increased download timeout to 600 seconds (10 minutes)
        'CONCURRENT_REQUESTS': 8,  # Adjusted concurrent requests if necessary
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,  # Adjusted concurrent requests per domain if necessary
        'AUTOTHROTTLE_ENABLED': True,  # Enables automatic throttling
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 4,  # Target concurrency for automatic throttling
        'AUTOTHROTTLE_START_DELAY': 5,  # Initial delay for automatic throttling
        'AUTOTHROTTLE_MAX_DELAY': 60,  # Maximum delay for automatic throttling
        'AUTOTHROTTLE_DEBUG': True,  # Enables autothrottle debug mode
        #'LOG_LEVEL': 'INFO',  # Adjusted log level for more detailed logging
        #'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',  # Updated log file name
        }

    page = 0
    count = 0
    
    conn = psycopg2.connect(
        dbname="retailifydb",
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
        for main_category, sub_categories in self.cat_products_urls.items():
            for sub_category, product_url in sub_categories.items():
                catalogue_code = self.get_catalogue_code(main_category)
                if catalogue_code:
                    yield scrapy.Request(url=product_url, headers=self.headers, meta={'category': main_category, 'sub_category': sub_category, 'cat_url': product_url, 'page': self.page, 'catalogue_code': catalogue_code})

    def parse(self, response):
        #print("INSIDE PARSE")
        vendor_code = self.vendor_code
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        catalogue_code = response.meta['catalogue_code']
        page = response.meta['page']
        links = response.xpath('//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]/@href')
        for link in links:
            url = link.get()
            url = self.main_url + url 
            yield scrapy.Request(url=url, callback=self.parse_product, headers=self.headers, meta={'category': category, 'sub_category': sub_category, 'url': url, 'page': page, 'VendorCode': vendor_code, 'catalogue_code': catalogue_code})

        #NEXT PAGE
        next_page_url = response.xpath('//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]/@href').get()
        if next_page_url:
            next_page_url = self.main_url + next_page_url
            page = page + 1
            print("#################################################################")
            print(next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse, headers=self.headers, meta={'category': category, 'sub_category': sub_category, 'page': page, 'catalogue_code': catalogue_code})


    def parse_product(self, response):
        item = ProductItemAmazon()
        item['CatalogueName'] = response.meta['category']
        #item['CategoryName'] = response.xpath('(//span[@class="a-list-item"]/a[@class="a-link-normal a-color-tertiary"])[last()]/text()').get()
        item['CategoryName'] = response.meta['sub_category']
        page = response.meta['page']
        item['URL'] = response.meta['url']
        item['SKU'] = re.search(r'/dp/([^/]+)', response.url).group(1) if re.search(r'/dp/([^/]+)', response.url) else ''
        item['ProductName'] = response.xpath('//span[@id="productTitle"]/text()').get()

        if item['ProductName']:
            item['ProductName'] = item['ProductName'].strip()

        if not item['ProductName']:
            item['ProductName'] = ''

        item['RatingValue'] = response.xpath('//a[@class="a-popover-trigger a-declarative"]/span[@class="a-size-base a-color-base"]/text()').get()
        if not item['RatingValue']:
            item['RatingValue'] = 0

        if item['RatingValue']:
            item['RatingValue'] = str(item['RatingValue']).strip()
            item['RatingValue'] = round(float(item['RatingValue']), 2)

        #item['total_ratings'] = response.xpath('//span[@id="acrCustomerReviewText"]/text()').get()
        #if not item['total_ratings']:
            #item['total_ratings'] = 0
        
        item['MainImage'] = response.xpath('//img[@id="landingImage"]/@src').get()
        if not item['MainImage']:
            item['MainImage'] = ''

        price_in_aed = response.xpath('//span[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]/span/span[@class="a-price-whole"]/text()').get()
        if price_in_aed:
            price_in_aed_decimal = response.xpath('//span[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]/span/span[@class="a-price-fraction"]/text()').get()
            item['Offer'] = str(price_in_aed)+ '.' +str(price_in_aed_decimal)
            item['Offer'] = item['Offer'].replace(',', '')
            item['Offer'] = round(float(item['Offer']), 2)
        else:
            item['Offer'] = 0

        item['RegularPrice'] = response.xpath('//span[@class="a-size-small aok-offscreen"]/text()').get()
        if not item['RegularPrice']:
            item['RegularPrice'] = 0

        if item['RegularPrice']:
            item['RegularPrice'] = item['RegularPrice'].split('AED')[1].strip()
            item['RegularPrice'] = item['RegularPrice'].replace(',', '')
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)
            

        stock_avilability = response.xpath('//div[@id="availability"]/span[@class="a-size-medium a-color-success"]/text()').get()
        if stock_avilability:
            item['StockAvailability'] = True
        else:
            item['StockAvailability'] = True

        item['VendorCode'] = response.meta['VendorCode']
        item['BrandName'] = ''
        item['BrandCode'] = ''
        item['Currency'] = 'AED'
        item['About'] = response.xpath('//div[@id="renewedProgramDescriptionAtf"]/p/text()').get()
        catalogue_code = response.meta['catalogue_code']
        category_code = self.get_category_code(item['CategoryName'], catalogue_code)
        item['CatalogueCode'] = catalogue_code
        item['CategoryCode'] = category_code
        

        #savings_perc = response.xpath('//span[@class="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage"]/text()').get()
        #if not savings_perc:
        #    savings_perc = ''

        yield item

    
        # review_url = response.xpath('(//a[@data-hook="see-all-reviews-link-foot"])[last()]/@href').get()
        # if review_url:
        #     review_url = self.main_url + review_url
        #     yield scrapy.Request(url=review_url, headers=self.headers, callback=self.parse_review, meta={'item': item})

        # else:
        #     yield item


    def parse_review(self, response):
        item = response.meta['item']
        item_reviews = []

        for review in response.xpath("//div[@data-hook='review']"):
            comment = review.xpath(".//span[@data-hook='review-body']/span/text()").get()
            source = ''
            comment_date = review.xpath(".//span[@data-hook='review-date']/text()").get()
            comment_date = re.search(r'Reviewed in (.+) on (\d+\s+\w+\s+\d{4})', comment_date).group(2) if comment_date else None
            comment_date = datetime.strptime(comment_date, "%d %B %Y")
            comment_date = comment_date.strftime("%Y-%m-%d")
            rating = review.xpath(".//i[@data-hook='review-star-rating']/span/text()").get()
            rating = re.search(r'(\d+\.\d+)', rating).group(1) if rating else 0
            max_rating = round(5, 2)

            review_data = {
                    'Comment': comment,
                    'Source': source,
                    'CommentDate': comment_date,
                    'rating': round(float(rating), 2),
                    'max_rating': max_rating,
                    'average_rating': item['RatingValue']
                }
            item_reviews.append(review_data)
        item['reviews'] = item_reviews



        yield item

            




