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
import mysql.connector


class AmazonSpider(Spider):
    name = 'amazon'
    allowed_domains = ['www.amazon.ae']
    main_url = 'https://www.amazon.ae'

    cat_products_urls = {
                'Mobile Phones': 'https://www.amazon.ae/s?rh=n%3A12303750031&fs=true&ref=lp_12303750031_sar',
                'Mobile Accessories': 'https://www.amazon.ae/s?rh=n%3A12303803031&fs=true&ref=lp_12303803031_sar',
                'Computers': 'https://www.amazon.ae/s?rh=n%3A11497745031&fs=true&ref=lp_11497745031_sar',
                'Computer Accessories': 'https://www.amazon.ae/s?rh=n%3A12050239031&fs=true&ref=lp_12050239031_sar',
                'Printers and Ink': 'https://www.amazon.ae/s?rh=n%3A12050248031&fs=true&ref=lp_12050248031_sar',
                'Office and School Supplies': 'https://www.amazon.ae/s?rh=n%3A15150350031&fs=true&ref=lp_15150350031_sar',
                'Electronics': 'https://www.amazon.ae/s?rh=n%3A11601326031&ref=lp_11601327031_sar',
                'Appliances': 'https://www.amazon.ae/s?rh=n%3A15149780031&ref=lp_15149781031_sar',
                'Women Watch': 'https://www.amazon.ae/s?rh=n%3A11995894031&fs=true&ref=lp_11995894031_sar',
                'Women Jewelry': 'https://www.amazon.ae/s?rh=n%3A11995892031&fs=true&ref=lp_11995892031_sar',
                'Women Sportswear': 'https://www.amazon.ae/s?rh=n%3A11996189031&fs=true&ref=lp_11996189031_sar',
                'Women Lingerie': 'https://www.amazon.ae/s?rh=n%3A11996199031&fs=true&ref=lp_11996199031_sar',
                'Women Outlet': 'https://www.amazon.ae/s?bbn=21648677031&rh=n%3A11497631031%2Cn%3A%2111497636031%2Cn%3A%2111497638031%2Cn%3A%2121611470031%2Cn%3A%2121611471031%2Cn%3A%2121648675031%2Cn%3A%2121648676031%2Cn%3A21648677031%2Cn%3A11995849031&dc&fst=as%3Aoff&qid=1611475788&rnid=11497632031&ref=nav_em_sl_w_outlet_0_2_8_7',
                'Women Shoes': 'https://www.amazon.ae/s?rh=n%3A11995893031&fs=true&ref=lp_11995893031_sar',
                'Women Travel Bags and Backpacks': 'https://www.amazon.ae/gp/browse.html?node=11995843031&ref_=nav_em_sl_luggage_back_0_2_8_10',
                'Women Bags and Wallets': 'https://www.amazon.ae/gp/browse.html?node=11995891031&ref_=nav_em_sl_w_bags_wallets_0_2_8_11',
                'Women Eyewear': 'https://www.amazon.ae/s?rh=n%3A11996178031&fs=true&ref=lp_11996178031_sar',
                'Women Sports Shoes': 'https://www.amazon.ae/gp/browse.html?node=11996234031&ref_=nav_em_sl_w_shoes_spt_0_2_8_13',
                
                'Men Shoes': 'https://www.amazon.ae/s?rh=n%3A11995876031&fs=true&ref=lp_11995876031_sar',
                'Men Bags and Wallets': 'https://www.amazon.ae/gp/browse.html?node=11995874031&ref_=nav_em_sl_m_bags_wallets_0_2_9_10',
                'Men Eyewear': 'https://www.amazon.ae/s?rh=n%3A11996046031&fs=true&ref=lp_11996046031_sar',
                'Men Travel Bags and Backpacks': 'https://www.amazon.ae/gp/browse.html?node=11995843031&ref_=nav_em_sl_luggage_back_0_2_9_12',
                'Men Sports Shoes': 'https://www.amazon.ae/s?rh=n%3A11996088031&fs=true&ref=lp_11996088031_sar',
                'Men Watch': 'https://www.amazon.ae/s?rh=n%3A11995877031&fs=true&ref=lp_11995877031_sar',
                'Men Sportswear': 'https://www.amazon.ae/s?rh=n%3A11996059031&fs=true&ref=lp_11996059031_sar',
                'Men Accessories': 'https://www.amazon.ae/gp/browse.html?node=11995872031&ref_=nav_em_sl_m_accessories_0_2_9_5',
                'Men Underwear': 'https://www.amazon.ae/gp/browse.html?node=11996075031&ref_=nav_em_sl_m_underwear_0_2_9_6',
                'Men Outlet': 'https://www.amazon.ae/s?bbn=21648677031&rh=n%3A11497631031%2Cn%3A%2111497636031%2Cn%3A%2111497638031%2Cn%3A%2121611470031%2Cn%3A%2121611471031%2Cn%3A%2121648675031%2Cn%3A%2121648676031%2Cn%3A21648677031%2Cn%3A11995844031&dc&fst=as%3Aoff&qid=1611475788&rnid=11497632031&ref=nav_em_sl_m_outlet_0_2_9_7',

                'Boys Clothing': 'https://www.amazon.ae/gp/browse.html?node=11995853031&ref_=nav_em_sl_b_clothing_0_2_10_2',
                'Girls Clothing': 'https://www.amazon.ae/gp/browse.html?node=11995859031&ref_=nav_em_sl_g_clothing_0_2_10_3',
                'Kids Watches': 'https://www.amazon.ae/s?rh=n%3A21720575031&fs=true&ref=lp_21720575031_sar',
                'Boys Shoes': 'https://www.amazon.ae/gp/browse.html?node=11995856031&ref_=nav_em_sl_b_shoes_0_2_10_6',
                'Girls Shoes': 'https://www.amazon.ae/gp/browse.html?node=11995862031&ref_=nav_em_sl_g_shoes_0_2_10_7',
                'School Bags': 'https://www.amazon.ae/gp/browse.html?node=11996021031&ref_=nav_em_sl_k_bags_0_2_10_8',
                'Beauty': 'https://www.amazon.ae/s?rh=n%3A11497859031&fs=true&ref=lp_11497859031_sar',
                'Perfumes': 'https://www.amazon.ae/s?rh=n%3A12149479031&fs=true&ref=lp_12149479031_sar',
                'Health and Personal Care': 'https://www.amazon.ae/s?rh=n%3A18050412031&fs=true&ref=lp_18050412031_sar',
                'Food and Beverages': 'https://www.amazon.ae/s?rh=n%3A15150008031&fs=true&ref=lp_15150008031_sar',
                'Home Care': 'https://www.amazon.ae/s?rh=n%3A15159997031&fs=true&ref=lp_15159997031_sar',
                'Home': 'https://www.amazon.ae/s?rh=n%3A16725681031&fs=true&ref=lp_16725681031_sar',
                'Kitchen and Dining': 'https://www.amazon.ae/s?rh=n%3A16402718031&fs=true&ref=lp_16402718031_sar',
                'Pet Supplies': 'https://www.amazon.ae/s?rh=n%3A15150407031&fs=true&ref=lp_15150407031_sar',
                'Tools and Home Improvement': 'https://www.amazon.ae/s?rh=n%3A11601269031&fs=true&ref=lp_11601269031_sar',
                'Baby Products': 'https://www.amazon.ae/s?rh=n%3A11498087031&fs=true&ref=lp_11498087031_sar',
                'Kids Fashion': 'https://www.amazon.ae/s?rh=n%3A15387144031&fs=true&ref=lp_15387144031_sar',
                'Baby Fashion': 'https://www.amazon.ae/gp/browse.html?node=11995840031&ref_=nav_em_sl_baby_fashion_0_2_15_9',
                'Toys and Games': 'https://www.amazon.ae/s?rh=n%3A17930529031&fs=true&ref=lp_17930529031_sar',
                'Sports, Fitness and Outdoor': 'https://www.amazon.ae/gp/browse.html?node=11601213031&ref_=nav_em_spt_all_0_2_16_2',
                'Books': 'https://www.amazon.ae/s?rh=n%3A11497688031&fs=true&ref=lp_11497688031_sar',
                'Video Games': 'https://www.amazon.ae/s?rh=n%3A11601383031&fs=true&ref=lp_11601383031_sar',
                'Automotive': 'https://www.amazon.ae/s?rh=n%3A11498030031&fs=true&ref=lp_11498030031_sar'

 
        }

    custom_settings = {
        'DOWNLOAD_DELAY': 0.2,
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 10,
        'LOG_FILE': f'scrapy-logs/{name}-{datetime.now().strftime("%d-%m-%y-%H-%M-%S")}.log',
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    page = 0
    count = 0
    
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
        for category, product_url in self.cat_products_urls.items():
            catalogue_code = self.get_catalogue_code(category)
            if catalogue_code:
                yield scrapy.Request(url=product_url, meta={'category': category, 'catalogue_code': catalogue_code, 'page': self.page})



    def parse(self, response):
        #print("INSIDE PARSE")
        vendor_code = self.vendor_code
        category = response.meta['category']
        catalogue_code = response.meta['catalogue_code']
        page = response.meta['page']
        links = response.xpath('//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]/@href')
        for link in links:
            url = link.get()
            url = self.main_url + url
            
            yield scrapy.Request(url=url, callback=self.parse_product, meta={'category': category, 'url': url, 'page': page, 'VendorCode': vendor_code, 'catalogue_code': catalogue_code})

        #NEXT PAGE
        next_page_url = response.xpath('//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]/@href').get()
        if next_page_url:
            next_page_url = self.main_url + next_page_url
            page = page + 1
            print("#################################################################")
            print(next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse, meta={'category': category, 'page': page, 'catalogue_code': catalogue_code})


    def parse_product(self, response):
        item = ProductItemAmazon()
        item['CatalogueName'] = response.meta['category']
        item['CategoryName'] = response.xpath('(//span[@class="a-list-item"]/a[@class="a-link-normal a-color-tertiary"])[last()]/text()').get()
        item['CategoryName'] = item['CategoryName'].strip()
        page = response.meta['page']
        item['URL'] = response.meta['url']
        item['SKU'] = re.search(r'/dp/([^/]+)', response.url).group(1) if re.search(r'/dp/([^/]+)', response.url) else ''
        item['ProductName'] = response.xpath('//span[@id="productTitle"]/text()').get()
        if not item['ProductName']:
            item['ProductName'] = ''

        if item['ProductName']:
            item['ProductName'] = item['ProductName'].strip()

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
        catalogue_code = response.meta['catalogue_code']
        category_code = self.get_category_code(item['CategoryName'], catalogue_code)
        item['CatalogueCode'] = catalogue_code
        item['CategoryCode'] = category_code
        

        #savings_perc = response.xpath('//span[@class="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage"]/text()').get()
        #if not savings_perc:
        #    savings_perc = ''

    
        review_url = response.xpath('(//a[@data-hook="see-all-reviews-link-foot"])[last()]/@href').get()
        if review_url:
            review_url = self.main_url + review_url
            yield scrapy.Request(url=review_url, callback=self.parse_review, meta={'item': item})

        else:
            yield item


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

            




