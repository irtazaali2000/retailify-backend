import re

import requests
from scrapy.spiders import Spider, CrawlSpider, Request
import json
from scrapy.selector import Selector
import logging
from datetime import datetime

from ..settings import HOST, CATALOGUE_URL_T
from ..items import ProductItemAsterPharmacy
from ecom_crawlers.utils import *
from fake_useragent import UserAgent
import scrapy
import copy
import mysql.connector



class AsterPharmacySpider(Spider):
    name = 'asterpharmacy'
    allowed_domains = ['myaster.com']
    main_url = 'https://www.myaster.com'
    main_url_img = 'https://1astercommercemedia.azureedge.net/catalog/product/1/0/{}_2.jpg'
    products_url = 'https://www.myaster.com/online-pharmacy/c/nutrition/2058?page={}'
    headers = {'Content-Type': 'application/json'}
    

    custom_settings = {
        'DOWNLOAD_DELAY': 0.50,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 200,
                #'LOG_STDOUT': False,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    page = 1
    count = 0
    
    categories = {
        "Mother And Baby": {
            "Baby Diapering": "https://www.myaster.com/online-pharmacy/c/baby-diapering/3382?page={}",
            "Baby Bath and Skin Care": "https://www.myaster.com/online-pharmacy/c/baby-bath-skin-care/3388?page={}",
            "Baby Feeding Accessories": "https://www.myaster.com/online-pharmacy/c/baby-feeding-accessories/3396?page={}",
            "Moms and Maternity": "https://www.myaster.com/online-pharmacy/c/moms-maternity/3400?page={}",
            "Baby Toys and Accessories": "https://www.myaster.com/online-pharmacy/c/baby-toys-accessories/3406?page={}",
            "Baby Food and Supplement": "https://www.myaster.com/online-pharmacy/c/baby-food-supplements/3408?page={}",
            "Kids Food and Supplement": "https://www.myaster.com/online-pharmacy/c/kids-food-supplements/3410?page={}",
            "Baby Health and Safety": "https://www.myaster.com/online-pharmacy/c/baby-health-safety/3416?page={}",
            "Baby Medical Essentials": "https://www.myaster.com/online-pharmacy/c/baby-medical-essentials/3421?page={}"
        },
        "Beauty": {
            "Skin Care": "https://www.myaster.com/online-pharmacy/c/skin-care/3728?page={}",
            "Bath and Body Care": "https://www.myaster.com/online-pharmacy/c/bath-and-body-care/3730?page={}",
            "Hair Care": "https://www.myaster.com/online-pharmacy/c/hair-care/3736?page={}",
            "Sun Protection": "https://www.myaster.com/online-pharmacy/c/sun-protection/3740?page={}",
            "Make Up": "https://www.myaster.com/online-pharmacy/c/make-up/3746?page={}",
            "Hand and Foot Care": "https://www.myaster.com/online-pharmacy/c/hand-and-foot-care/3752?page={}",
            "Kits and Combos": "https://www.myaster.com/online-pharmacy/c/kits-and-combos/3761?page={}",
            "Fragrance": "https://www.myaster.com/online-pharmacy/c/fragrance/3803?page={}"
        },
        "Nutrition": {
            "Health Concern": "https://www.myaster.com/online-pharmacy/c/health-concern/2059?page={}",
            "Fish Oils and Omega": "https://www.myaster.com/online-pharmacy/c/fish-oils-omega/2065?page={}",
            "Children's Supplements": "https://www.myaster.com/online-pharmacy/c/children-s-supplements/2070?page={}",
            "Vitamins and Minerals": "https://www.myaster.com/online-pharmacy/c/vitamins-minerals/2075?page={}",
            "Speciality Supplements": "https://www.myaster.com/online-pharmacy/c/speciality-supplements/2166?page={}",
            "Herbals and Botanicals": "https://www.myaster.com/online-pharmacy/c/herbals-botanicals/2257?page={}",
            "Sports Nutrition": "https://www.myaster.com/online-pharmacy/c/sports-nutrition/2262?page={}"
        },
        "Equipment and Homecare": {
            "Grooming and Beauty Equipment": "https://www.myaster.com/online-pharmacy/c/grooming-beauty-equipment/1912?page={}",
            "Baby Equipment": "https://www.myaster.com/online-pharmacy/c/baby-equipment/1942?page={}",
            "Respiratory Care": "https://www.myaster.com/online-pharmacy/c/respiratory-care/1946?page={}",
            "Bath and Shower Support": "https://www.myaster.com/online-pharmacy/c/bath-shower-support/1951?page={}",
            "Dental Equipment": "https://www.myaster.com/online-pharmacy/c/dental-equipment/1955?page={}",
            "Massagers": "https://www.myaster.com/online-pharmacy/c/massagers/1970?page={}",
            "Health Monitors": "https://www.myaster.com/online-pharmacy/c/health-monitors/1977?page={}",
            "Professional Equipment": "https://www.myaster.com/online-pharmacy/c/professional-equipment/1982?page={}",
            "Hearing Aid": "https://www.myaster.com/online-pharmacy/c/hearing-aid/1999?page={}",
            "Heat Therapy": "https://www.myaster.com/online-pharmacy/c/heat-therapy/2000?page={}",
            "Homecare Bed and Accessories": "https://www.myaster.com/online-pharmacy/c/homecare-bed-accessories/2005?page={}",
            "Mobility Support": "https://www.myaster.com/online-pharmacy/c/mobility-support/2013?page={}",
            "Orthopedic Supports": "https://www.myaster.com/online-pharmacy/c/orthopedic-supports/2020?page={}",
            "Physiotherapy": "https://www.myaster.com/online-pharmacy/c/physiotherapy/2044?page={}"
        },
        "Medical Essentials": {
            "Derma Health": "https://www.myaster.com/online-pharmacy/c/derma-health/1823",
            "Cold and Flu": "https://www.myaster.com/online-pharmacy/c/cold-flu/1966",
            "Pain and Fever": "https://www.myaster.com/online-pharmacy/c/pain-fever/1997",
            "First Aid": "https://www.myaster.com/online-pharmacy/c/first-aid/2052",
            "Medical Supplies and Disposables": "https://www.myaster.com/online-pharmacy/c/medical-supplies-disposables/2077",
            "Medicine Aid": "https://www.myaster.com/online-pharmacy/c/medicine-aid/2079",
            "Ayurveda": "https://www.myaster.com/online-pharmacy/c/ayurveda/2134",
            "Digestive Remedies": "https://www.myaster.com/online-pharmacy/c/digestive-remedies/2140",
            "Eye Health": "https://www.myaster.com/online-pharmacy/c/eye-health/2147",
            "Cough and Sore Throat": "https://www.myaster.com/online-pharmacy/c/cough-sore-throat/2149",
            "Oral Health": "https://www.myaster.com/online-pharmacy/c/oral-health/2155",
            "Ear Care": "https://www.myaster.com/online-pharmacy/c/ear-care/2173",
            "Electrolytes and Rehydration": "https://www.myaster.com/online-pharmacy/c/electrolytes-rehydration/2177",
            "Homeopathy": "https://www.myaster.com/online-pharmacy/c/homeopathy/2189",
            "Nutrition Support": "https://www.myaster.com/online-pharmacy/c/nutrition-support/2212",
            "Urinary Bladder Health": "https://www.myaster.com/online-pharmacy/c/urinary-bladder-health/2217",
            "Urinary": "https://www.myaster.com/online-pharmacy/c/urinary/4319"
        },
        "Personal Care": {
            "Personal Hygiene": "https://www.myaster.com/online-pharmacy/c/personal-hygiene/1832",
            "Mens Care": "https://www.myaster.com/online-pharmacy/c/mens-care/1886",
            "Nail Care": "https://www.myaster.com/online-pharmacy/c/nail-care/1890",
            "Personal Grooming": "https://www.myaster.com/online-pharmacy/c/personal-grooming/1894",
            "Foot Care": "https://www.myaster.com/online-pharmacy/c/foot-care/1933",
            "Womens Care": "https://www.myaster.com/online-pharmacy/c/womens-care/1963",
            "Travel Essentials": "https://www.myaster.com/online-pharmacy/c/travel-essentials/1972",
            "Sexual Wellness": "https://www.myaster.com/online-pharmacy/c/sexual-wellness/2090",
            "Eye Care": "https://www.myaster.com/online-pharmacy/c/eye-care/2180",
            "Oral Care": "https://www.myaster.com/online-pharmacy/c/oral-care/3516"
        },
        "Lifestyle and Fitness": {
            "Fitness and Exercise": "https://www.myaster.com/online-pharmacy/c/fitness-exercise/1990",
            "Sleep and Relaxation": "https://www.myaster.com/online-pharmacy/c/sleep-relaxation/2034",
            "Aromatherapy": "https://www.myaster.com/online-pharmacy/c/aromatherapy/2107",
            "Fragrance": "https://www.myaster.com/online-pharmacy/c/fragrance/2123",
            "Health Food and Beverages": "https://www.myaster.com/online-pharmacy/c/health-food-beverages/2124"
        },

        "Health Condition": {
            "Specialist Skincare": "https://www.myaster.com/online-pharmacy/c/specialist-skincare/1819",
            "Hair Problems": "https://www.myaster.com/online-pharmacy/c/hair-problems/1923",
            "Pregnancy and Breastfeeding": "https://www.myaster.com/online-pharmacy/c/pregnancy-breastfeeding/1944",
            "Cough, Cold and Flu": "https://www.myaster.com/online-pharmacy/c/cough-cold-flu/1950",
            "Blood Pressure": "https://www.myaster.com/online-pharmacy/c/blood-pressure/1980",
            "Diabetes": "https://www.myaster.com/online-pharmacy/c/diabetes/1981",
            "Heart Health": "https://www.myaster.com/online-pharmacy/c/heart-health/1984",
            "Cholesterol Support": "https://www.myaster.com/online-pharmacy/c/cholesterol-support/1986",
            "Respiratory Health": "https://www.myaster.com/online-pharmacy/c/respiratory-health/1988",
            "Pain and Inflammation": "https://www.myaster.com/online-pharmacy/c/pain-inflammation/2003",
            "Circulation Support": "https://www.myaster.com/online-pharmacy/c/circulation-support/2027",
            "Bone and Joint": "https://www.myaster.com/online-pharmacy/c/bone-joint/2033",
            "Allergy and Hay Fever": "https://www.myaster.com/online-pharmacy/c/allergy-hay-fever/2057",
            "Immunity": "https://www.myaster.com/online-pharmacy/c/immunity/2062",
            "Brain and Memory": "https://www.myaster.com/online-pharmacy/c/brain-memory/2067",
            "Energy and Wellbeing": "https://www.myaster.com/online-pharmacy/c/energy-wellbeing/2083",
            "Eye Health": "https://www.myaster.com/online-pharmacy/c/eye-health/2085",
            "Menopause Support": "https://www.myaster.com/online-pharmacy/c/menopause-support/2089",
            "Mens Health": "https://www.myaster.com/online-pharmacy/c/mens-health/2092",
            "Fertility": "https://www.myaster.com/online-pharmacy/c/fertility/2093",
            "Womens Health": "https://www.myaster.com/online-pharmacy/c/womens-health/2095",
            "Smoking Cessation": "https://www.myaster.com/online-pharmacy/c/smoking-cessation/2102",
            "Weight Loss": "https://www.myaster.com/online-pharmacy/c/weight-loss/2103",
            "Digestion and Detox": "https://www.myaster.com/online-pharmacy/c/digestion-detox/2105",
            "Sleep Support": "https://www.myaster.com/online-pharmacy/c/sleep-support/2110",
            "Stress Relief": "https://www.myaster.com/online-pharmacy/c/stress-relief/2111",
            "Kidney Health": "https://www.myaster.com/online-pharmacy/c/kidney-health/2135",
            "Liver Support": "https://www.myaster.com/online-pharmacy/c/liver-support/2137",
            "Dental and Oral Care": "https://www.myaster.com/online-pharmacy/c/dental-oral-care/2158",
            "Mood Support": "https://www.myaster.com/online-pharmacy/c/mood-support/2248",
            "Foot Care": "https://www.myaster.com/online-pharmacy/c/foot-care/2287"
        }}

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
    cursor = conn.cursor()

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
        # Attempt to retrieve the catalogue code from the database
        query = "SELECT CatalogueCode FROM product_catalogue WHERE CatalogueName = %s"
        self.cursor.execute(query, (catalogue_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the catalogue code exists, return it
            return result[0]
        else:
            # If the catalogue code doesn't exist, insert it into the database
            insert_query = "INSERT INTO product_catalogue (CatalogueName) VALUES (%s)"
            self.cursor.execute(insert_query, (catalogue_name,))
            self.conn.commit()  # Commit the transaction
            
            # Retrieve the newly inserted catalogue code
            self.cursor.execute(query, (catalogue_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
    
    def get_category_code(self, category_name, catalogue_code):
        # Attempt to retrieve the category code from the database
        query = "SELECT CategoryCode FROM product_category WHERE CategoryName = %s"
        self.cursor.execute(query, (category_name,))
        result = self.cursor.fetchone()
        
        if result:
            # If the category code exists, return it
            return result[0]
        else:
            # If the category code doesn't exist, insert it into the database
            insert_query = "INSERT INTO product_category (CategoryName, CatalogueCode_id) VALUES (%s, %s)"
            self.cursor.execute(insert_query, (category_name, catalogue_code))
            self.conn.commit()  # Commit the transaction
            
            # Retrieve the newly inserted category code
            self.cursor.execute(query, (category_name,))
            result = self.cursor.fetchone()
            # print("*******************")
            # print(result[0])
            return result[0] if result else None

    def start_requests(self):
        for main_category, sub_categories in self.categories.items():
            catalogue_code = self.get_catalogue_code(main_category)
            if catalogue_code:
                for sub_category, sub_category_url in sub_categories.items():
                    yield scrapy.Request(url=sub_category_url.format(self.page),
                                        meta={'page': self.page, 'category': main_category, 'sub_category': sub_category, 'sub_category_url': sub_category_url, 'catalogue_code': catalogue_code})


    def parse(self, response):
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        sub_category_url = response.meta['sub_category_url']
        catalogue_code = response.meta['catalogue_code']
        vendor_code = self.vendor_code
        page = response.meta['page']
        links = response.xpath('//div[@class="item"]/a/@href').getall()
        for link in links:
            url = self.main_url + link
            
            yield scrapy.Request(url=url, callback=self.parse_product,
                                 meta={'page': page, 'category': category, 'sub_category': sub_category, 'url': url, 'vendor_code': vendor_code, 'catalogue_code': catalogue_code})

        #NEXT PAGE
        page = page + 1
        yield scrapy.Request(url=sub_category_url.format(page), callback=self.parse, meta={'page': page, 'category': category, 'sub_category': sub_category, 'sub_category_url': sub_category_url, 'catalogue_code': catalogue_code})


    def parse_product(self, response):
        item = ProductItemAsterPharmacy()
        item['CatalogueName'] = response.meta['category']
        item['CategoryName'] = response.meta['sub_category']
        vendor_code = response.meta['vendor_code']
        item['URL'] = response.meta['url']
        sku = response.meta['url']
        item['SKU'] = sku.split("/")[-1]
        item['ProductName'] = response.xpath("//div[@class='productName']/text()").get()
        item['RegularPrice'] = response.xpath('(//div[@class="priceContainer"]/div[@class="priceWrapper"]/div[@class="price"]/span/text())[last()]').get()
        
        if item['RegularPrice']:
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)
            item['Offer'] = response.xpath('(//div[@class="priceContainer"]/div[@class="priceWrapper"]/div[@class="price"]/text())')[2].get()
            item['Offer'] = round(float(item['Offer']), 2)
        else:
            item['RegularPrice'] = response.xpath('(//div[@class="priceContainer"]/div[@class="priceWrapper"]/div[@class="price"]/text())[last()]').get()
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)
            item['Offer'] = 0
        
        item['BrandName'] = response.xpath('//div[@class="brandName"]/a/text()').get()
        item['MainImage'] = self.main_url_img.format(item['SKU'])
        
        item['StockAvailability'] = response.xpath("//div[@class='stock']/text()").get()
        if item['StockAvailability']:
            item['StockAvailability'] = 1
        else:
            item['StockAvailability'] = 0
        
        item['BrandCode'] = ''
        item['ModelNumber'] = ''
        item['RatingValue'] = 0
        item['VendorCode'] = vendor_code
        catalogue_code = response.meta['catalogue_code']
        category_code = self.get_category_code(item['CategoryName'], catalogue_code)
        item['CatalogueCode'] = catalogue_code
        item['CategoryCode'] = category_code
        
        #page = response.meta['page']
        yield item