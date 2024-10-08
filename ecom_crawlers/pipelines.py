# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json

import requests
import logging
from datetime import datetime

from .settings import HOST
from scrapy.utils.project import get_project_settings
from .utils import sendemail, from_addr
from scrapy.exceptions import DropItem
from itemadapter import ItemAdapter
import re
from bs4 import BeautifulSoup


LOGGER = logging.getLogger(__name__)


class FilterItemPipeline(object):
    fields = ['URL', 'ProductName',]

    def process_item(self, item, spider):
        missing = [f for f in self.fields if not item[f]]
        if missing:
            raise DropItem("Dropping Item: {}".format(item))

        return item
    


####JUMBO#######################################
class FilterItemPipelineJumbo(object):
  

    def process_item(self, item, spider):
        if 'RegularPrice' in item and item['RegularPrice']:
            price = str(item['RegularPrice']).replace('AED','').replace(',','')            
            item['RegularPrice'] = float(price)

        if 'Offer' in item and item['Offer']:
            price = str(item['Offer']).replace('AED','').replace(',','')            
            item['Offer'] = float(price)
        
        # Clean 'About' field by removing HTML tags and special characters
        if 'About' in item and item['About']:
            soup = BeautifulSoup(item['About'], 'html.parser')
            clean_about = soup.get_text(separator=" ")  # Get clean text
            clean_about = re.sub(r'\s+', ' ', clean_about)  # Remove extra whitespace
            item['About'] = clean_about.strip()

        # if 'categories' in item and item['categories']:
        #     categories_str = ','.join(item['categories'])
        #     item['categories'] = categories_str
            
        return item

class UploadPipelineJumbo(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value
        self.seen_items = set()

    def process_item(self, item, spider):
        item_key = item.get('SKU')
        if item_key in self.seen_items:
            LOGGER.info(f"Item already processed: {item_key}")
            return item

        self.seen_items.add(item_key)
        try:
            #LOGGER.info(f"Sending item to API: {json.dumps(dict(item))}")
            res = requests.post(self.api, json=dict(item))
            #LOGGER.info(f"API response: {res.status_code} {res.text}")
            if res.status_code != 200:
                LOGGER.error(f"Product Not Uploaded: {res.text}")
                if self.email:
                    sendemail(self.email, self.to_email, f"Product Not Uploaded: {res.text}")
                return item
            self.seen_items.remove(item_key)
        except requests.RequestException as e:
            LOGGER.error(f"Request exception: {e}")
            if self.email:
                sendemail(self.email, self.to_email, f"Request exception: {e}")
            return item
        return item

    def open_spider(self, spider):
        if self.email:
            # subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            message = f"{spider.name} initiated at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Opened: Email Sent to {self.to_email}")

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        if self.email:
            subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            # subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            message = f"{spider.name} Closed at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}\n\n" \
                      f"Total Item Scraped from spider={stats.get('item_scraped_count', 0)}\n"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Closed: Email Sent to {self.to_email}")


######################FirstCry#######################################
class FilterItemPipelineFirstCry(object):
  

    def process_item(self, item, spider):
        if 'RegularPrice' in item and item['RegularPrice']:   
            item['RegularPrice'] = float(item['RegularPrice'])

        if 'RatingValue' in item and item['RatingValue']:
            item['RatingValue'] = float(item['RatingValue'])
            
        return item
    

class UploadPipelineFirstCry(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value

    def process_item(self, item, spider):
        # Send the data directly as a dictionary
        res = requests.post(
            self.api,
            json=dict(item)
        )

        if res.status_code != 200:
            LOGGER.error(f"Product Not Uploaded: {res.text}")
            if self.email:
                subject = f"{spider.name} : Product insertion has been failed due to {res.text}"
                message = f"Api Failed:" \
                          f"{res.text}\n\n\n" \
                          f"ITEM DETAILS BELOW:" \
                          f"{json.dumps(dict(item))}"

                sendemail(from_addr=from_addr,
                          to_addr_list=self.to_email,
                          cc_addr_list=["baig052@gmail.com"],
                          subject=subject,
                          message=message)
                LOGGER.error(f"Error Raised: Email Sent to {self.to_email}")

        res.raise_for_status()

        return item

    def open_spider(self, spider):
        if self.email:
            # subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            message = f"{spider.name} initiated at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Opened: Email Sent to {self.to_email}")

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        if self.email:
            subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            # subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            message = f"{spider.name} Closed at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}\n\n" \
                      f"Total Item Scraped from spider={stats.get('item_scraped_count', 0)}\n"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Closed: Email Sent to {self.to_email}")




######################  H and M  #######################################
class FilterItemPipelineHandM(object):
  

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if 'RegularPrice' in item and isinstance(item['RegularPrice'], str):  
            price_in_dollars = item['RegularPrice'].replace(' ', '').replace('$', '') 
            item['RegularPrice'] = float(price_in_dollars)


        if 'RatingValue' in item and item['RatingValue']:  
            item['RatingValue'] = round(float(item['RatingValue']), 2)


        discounted_price_in_dollars = adapter.get('Offer')
        if discounted_price_in_dollars == "":
            adapter['Offer'] = float(0)
        elif isinstance(discounted_price_in_dollars, str):
            discounted_price_in_dollars = discounted_price_in_dollars.replace(' ', '').replace('$', '')
            adapter['Offer'] = float(discounted_price_in_dollars)

            
        return item
    

class UploadPipelineHandM(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value

    def process_item(self, item, spider):
        # Send the data directly as a dictionary
        res = requests.post(
            self.api,
            json=dict(item)
        )

        if res.status_code != 200:
            LOGGER.error(f"Product Not Uploaded: {res.text}")
            if self.email:
                subject = f"{spider.name} : Product insertion has been failed due to {res.text}"
                message = f"Api Failed:" \
                          f"{res.text}\n\n\n" \
                          f"ITEM DETAILS BELOW:" \
                          f"{json.dumps(dict(item))}"

                sendemail(from_addr=from_addr,
                          to_addr_list=self.to_email,
                          cc_addr_list=["baig052@gmail.com"],
                          subject=subject,
                          message=message)
                LOGGER.error(f"Error Raised: Email Sent to {self.to_email}")

        res.raise_for_status()

        return item

    def open_spider(self, spider):
        if self.email:
            # subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            message = f"{spider.name} initiated at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Opened: Email Sent to {self.to_email}")

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        if self.email:
            subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            # subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            message = f"{spider.name} Closed at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}\n\n" \
                      f"Total Item Scraped from spider={stats.get('item_scraped_count', 0)}\n"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Closed: Email Sent to {self.to_email}")



######################  Boots  #######################################
class FilterItemPipelineBoots(object):
  

    def process_item(self, item, spider):
        #adapter = ItemAdapter(item)

        if 'Offer' in item and item['Offer']:  
            item['Offer'] = round(float(item['Offer']), 2)

        if 'RegularPrice' in item and item['RegularPrice']:  
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)

        if 'RatingValue' in item and item['RatingValue']:
            item['RatingValue'] = round(float(item['RatingValue']), 2)


        return item
    

class UploadPipelineBoots(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value

    def process_item(self, item, spider):
        # Send the data directly as a dictionary
        res = requests.post(
            self.api,
            json=dict(item)
        )

        if res.status_code != 200:
            LOGGER.error(f"Product Not Uploaded: {res.text}")
            if self.email:
                subject = f"{spider.name} : Product insertion has been failed due to {res.text}"
                message = f"Api Failed:" \
                          f"{res.text}\n\n\n" \
                          f"ITEM DETAILS BELOW:" \
                          f"{json.dumps(dict(item))}"

                sendemail(from_addr=from_addr,
                          to_addr_list=self.to_email,
                          cc_addr_list=["baig052@gmail.com"],
                          subject=subject,
                          message=message)
                LOGGER.error(f"Error Raised: Email Sent to {self.to_email}")

        res.raise_for_status()

        return item

    def open_spider(self, spider):
        if self.email:
            # subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            message = f"{spider.name} initiated at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Opened: Email Sent to {self.to_email}")

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        if self.email:
            subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            # subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            message = f"{spider.name} Closed at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}\n\n" \
                      f"Total Item Scraped from spider={stats.get('item_scraped_count', 0)}\n"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Closed: Email Sent to {self.to_email}")



######################  Centre Point  #######################################
class FilterItemPipelineCentrePoint(object):
    def process_item(self, item, spider):
        if 'Offer' in item and item['Offer']:  
            item['Offer'] = round(float(item['Offer']), 2)

        if 'RegularPrice' in item and item['RegularPrice']:  
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)

        if 'RatingValue' in item and item['RatingValue']:
            item['RatingValue'] = round(float(item['RatingValue']), 2)

        # if 'sub_categories' in item and item['sub_categories']:
        #     sub_categories_str = ', '.join(item['sub_categories'])
        #     item['sub_categories'] = sub_categories_str

        return item
    

class UploadPipelineCentrePoint(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value

    def process_item(self, item, spider):
        # Send the data directly as a dictionary
        res = requests.post(
            self.api,
            json=dict(item)
        )

        if res.status_code != 200:
            LOGGER.error(f"Product Not Uploaded: {res.text}")
            if self.email:
                subject = f"{spider.name} : Product insertion has been failed due to {res.text}"
                message = f"Api Failed:" \
                          f"{res.text}\n\n\n" \
                          f"ITEM DETAILS BELOW:" \
                          f"{json.dumps(dict(item))}"

                sendemail(from_addr=from_addr,
                          to_addr_list=self.to_email,
                          cc_addr_list=["baig052@gmail.com"],
                          subject=subject,
                          message=message)
                LOGGER.error(f"Error Raised: Email Sent to {self.to_email}")

        res.raise_for_status()

        return item

    def open_spider(self, spider):
        if self.email:
            # subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            message = f"{spider.name} initiated at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Opened: Email Sent to {self.to_email}")

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        if self.email:
            subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            # subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            message = f"{spider.name} Closed at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}\n\n" \
                      f"Total Item Scraped from spider={stats.get('item_scraped_count', 0)}\n"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Closed: Email Sent to {self.to_email}")







######################  Max  #######################################
class FilterItemPipelineMax(object):
    def process_item(self, item, spider):
        if 'Offer' in item and item['Offer']:  
            item['Offer'] = round(float(item['Offer']), 2)

        if 'RegularPrice' in item and item['RegularPrice']:  
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)

        if 'RatingValue' in item and item['RatingValue']:
            item['RatingValue'] = round(float(item['RatingValue']), 2)

        # if 'sub_categories' in item and item['sub_categories']:
        #     sub_categories_str = ', '.join(item['sub_categories'])
        #     item['sub_categories'] = sub_categories_str

        return item
    

class UploadPipelineMax(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value

    def process_item(self, item, spider):
        # Send the data directly as a dictionary
        res = requests.post(
            self.api,
            json=dict(item)
        )

        if res.status_code != 200:
            LOGGER.error(f"Product Not Uploaded: {res.text}")
            if self.email:
                subject = f"{spider.name} : Product insertion has been failed due to {res.text}"
                message = f"Api Failed:" \
                          f"{res.text}\n\n\n" \
                          f"ITEM DETAILS BELOW:" \
                          f"{json.dumps(dict(item))}"

                sendemail(from_addr=from_addr,
                          to_addr_list=self.to_email,
                          cc_addr_list=["baig052@gmail.com"],
                          subject=subject,
                          message=message)
                LOGGER.error(f"Error Raised: Email Sent to {self.to_email}")

        res.raise_for_status()

        return item

    def open_spider(self, spider):
        if self.email:
            # subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            message = f"{spider.name} initiated at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Opened: Email Sent to {self.to_email}")

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        if self.email:
            subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            # subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            message = f"{spider.name} Closed at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}\n\n" \
                      f"Total Item Scraped from spider={stats.get('item_scraped_count', 0)}\n"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Closed: Email Sent to {self.to_email}")



######################  Emax  #######################################
class FilterItemPipelineEmax(object):
    def process_item(self, item, spider):
        if 'Offer' in item and item['Offer']:  
            item['Offer'] = round(float(item['Offer']), 2)

        if 'RegularPrice' in item and item['RegularPrice']:  
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)

        # if 'Cost' in item and item['Cost']:  
        #     item['Cost'] = round(float(item['Cost']), 2)

        # if 'MyPrice' in item and item['MyPrice']:  
        #     item['MyPrice'] = round(float(item['MyPrice']), 2)

        # Clean 'About' field by removing HTML tags and special characters
        if 'About' in item and item['About']:
            soup = BeautifulSoup(item['About'], 'html.parser')
            clean_about = soup.get_text(separator=" ")  # Get clean text
            clean_about = re.sub(r'\s+', ' ', clean_about)  # Remove extra whitespace
            item['About'] = clean_about.strip()

        # if 'percentage_discount' in item and item['percentage_discount']:  
        #     item['percentage_discount'] = round(float(item['percentage_discount']), 2)


        return item
    

class UploadPipelineEmax(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value
        self.seen_items = set()

    def process_item(self, item, spider):
        item_key = item.get('SKU')
        if item_key in self.seen_items:
            LOGGER.info(f"Item already processed: {item_key}")
            return item

        self.seen_items.add(item_key)
        try:
            #LOGGER.info(f"Sending item to API: {json.dumps(dict(item))}")
            res = requests.post(self.api, json=dict(item))
            #LOGGER.info(f"API response: {res.status_code} {res.text}")
            if res.status_code != 200:
                LOGGER.error(f"Product Not Uploaded: {res.text}")
                if self.email:
                    sendemail(self.email, self.to_email, f"Product Not Uploaded: {res.text}")
                return item
            self.seen_items.remove(item_key)
        except requests.RequestException as e:
            LOGGER.error(f"Request exception: {e}")
            if self.email:
                sendemail(self.email, self.to_email, f"Request exception: {e}")
            return item
        return item

    def open_spider(self, spider):
        if self.email:
            # subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            message = f"{spider.name} initiated at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Opened: Email Sent to {self.to_email}")

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        if self.email:
            subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            # subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            message = f"{spider.name} Closed at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}\n\n" \
                      f"Total Item Scraped from spider={stats.get('item_scraped_count', 0)}\n"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Closed: Email Sent to {self.to_email}")




######################  Namshi  #######################################
class FilterItemPipelineNamshi(object):
    def process_item(self, item, spider):
        if 'RegularPrice' in item and item['RegularPrice']:  
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)

        if 'Offer' in item and item['Offer']:  
            item['Offer'] = round(float(item['Offer']), 2)

        if 'RatingValue' in item and item['RatingValue']:  
            item['RatingValue'] = round(float(item['RatingValue']), 2)

        # if 'percentage_discount' in item and item['percentage_discount']:  
        #     item['percentage_discount'] = round(float(item['percentage_discount']), 2)


        return item
    

class UploadPipelineNamshi(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value

    def process_item(self, item, spider):
        # Send the data directly as a dictionary
        res = requests.post(
            self.api,
            json=dict(item)
        )

        if res.status_code != 200:
            LOGGER.error(f"Product Not Uploaded: {res.text}")
            if self.email:
                subject = f"{spider.name} : Product insertion has been failed due to {res.text}"
                message = f"Api Failed:" \
                          f"{res.text}\n\n\n" \
                          f"ITEM DETAILS BELOW:" \
                          f"{json.dumps(dict(item))}"

                sendemail(from_addr=from_addr,
                          to_addr_list=self.to_email,
                          cc_addr_list=["baig052@gmail.com"],
                          subject=subject,
                          message=message)
                LOGGER.error(f"Error Raised: Email Sent to {self.to_email}")

        res.raise_for_status()

        return item

    def open_spider(self, spider):
        if self.email:
            # subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            message = f"{spider.name} initiated at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Opened: Email Sent to {self.to_email}")

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        if self.email:
            subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            # subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            message = f"{spider.name} Closed at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}\n\n" \
                      f"Total Item Scraped from spider={stats.get('item_scraped_count', 0)}\n"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Closed: Email Sent to {self.to_email}")



    ######################  Life Pharmacy  #######################################
class FilterItemPipelineLifePharmacy(object):
    def process_item(self, item, spider):
        if 'Offer' in item and item['Offer']:  
            item['Offer'] = round(float(item['Offer']), 2)

        if 'RegularPrice' in item and item['RegularPrice']:  
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)

        if 'RatingValue' in item and item['RatingValue']:  
            item['RatingValue'] = round(float(item['RatingValue']), 2)

        # if 'max_salable_qty' in item and item['max_salable_qty']:  
        #     item['max_salable_qty'] = int(item['max_salable_qty'])


        return item
    

class UploadPipelineLifePharmacy(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value

    def process_item(self, item, spider):
        # Send the data directly as a dictionary
        res = requests.post(
            self.api,
            json=dict(item)
        )

        if res.status_code != 200:
            LOGGER.error(f"Product Not Uploaded: {res.text}")
            if self.email:
                subject = f"{spider.name} : Product insertion has been failed due to {res.text}"
                message = f"Api Failed:" \
                          f"{res.text}\n\n\n" \
                          f"ITEM DETAILS BELOW:" \
                          f"{json.dumps(dict(item))}"

                sendemail(from_addr=from_addr,
                          to_addr_list=self.to_email,
                          cc_addr_list=["baig052@gmail.com"],
                          subject=subject,
                          message=message)
                LOGGER.error(f"Error Raised: Email Sent to {self.to_email}")

        res.raise_for_status()

        return item
    


 ######################  Aster Pharmacy  #######################################
class FilterItemPipelineAsterPharmacy(object):
    def process_item(self, item, spider):
        if 'Offer' in item and item['Offer']:  
            item['Offer'] = round(float(item['Offer']), 2)

        if 'RegularPrice' in item and item['RegularPrice']:  
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)

        # if 'rating' in item and item['rating']:  
        #     item['rating'] = round(float(item['rating']), 2)

        # if 'matching_categories' in item and item['matching_categories']:
        #     matching_categories_str = ', '.join(item['matching_categories'])
        #     item['matching_categories'] = matching_categories_str

        # else:
        #     item['matching_categories'] = ''

        return item
    

class UploadPipelineAsterPharmacy(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value

    def process_item(self, item, spider):
        # Send the data directly as a dictionary
        res = requests.post(
            self.api,
            json=dict(item)
        )

        if res.status_code != 200:
            LOGGER.error(f"Product Not Uploaded: {res.text}")
            if self.email:
                subject = f"{spider.name} : Product insertion has been failed due to {res.text}"
                message = f"Api Failed:" \
                          f"{res.text}\n\n\n" \
                          f"ITEM DETAILS BELOW:" \
                          f"{json.dumps(dict(item))}"

                sendemail(from_addr=from_addr,
                          to_addr_list=self.to_email,
                          cc_addr_list=["baig052@gmail.com"],
                          subject=subject,
                          message=message)
                LOGGER.error(f"Error Raised: Email Sent to {self.to_email}")

        res.raise_for_status()

        return item
    


    ######################  Sharaf DG  #######################################
class FilterItemPipelineSharafDG(object):
    def process_item(self, item, spider):
        if 'Offer' in item and item['Offer']:  
            item['Offer'] = round(float(item['Offer']), 2)

        if 'RegularPrice' in item and item['RegularPrice']:  
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)

        # Clean 'About' field by removing HTML tags and special characters
        if 'About' in item and item['About']:
            soup = BeautifulSoup(item['About'], 'html.parser')
            clean_about = soup.get_text(separator="\n")  # Get text with line breaks
            # Replace multiple spaces or tabs with a single space
            clean_about = re.sub(r'[ \t]+', ' ', clean_about)
            # Replace multiple newlines with a single newline
            clean_about = re.sub(r'\n+', '\n', clean_about)
            item['About'] = clean_about.strip()
        

        if 'RatingValue' in item and item['RatingValue']:  
            item['RatingValue'] = round(float(item['RatingValue']), 2)

        if 'discount_value' in item and item['discount_value']:  
            item['discount_value'] = round(float(item['discount_value']), 2)

        if 'discount_percentage' in item and item['discount_percentage']:
            dicount_percentage_str = str(item['discount_percentage']) + '% OFF'
            item['discount_percentage'] = dicount_percentage_str

        return item
    

class UploadPipelineSharafDG(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value
        self.seen_items = set()

    def process_item(self, item, spider):
        item_key = item.get('SKU')
        if item_key in self.seen_items:
            LOGGER.info(f"Item already processed: {item_key}")
            return item

        self.seen_items.add(item_key)
        try:
            #LOGGER.info(f"Sending item to API: {json.dumps(dict(item))}")
            res = requests.post(self.api, json=dict(item))
            #LOGGER.info(f"API response: {res.status_code} {res.text}")
            if res.status_code != 200:
                LOGGER.error(f"Product Not Uploaded: {res.text}")
                if self.email:
                    sendemail(self.email, self.to_email, f"Product Not Uploaded: {res.text}")
                return item
            self.seen_items.remove(item_key)
        except requests.RequestException as e:
            LOGGER.error(f"Request exception: {e}")
            if self.email:
                sendemail(self.email, self.to_email, f"Request exception: {e}")
            return item
        return item

    def open_spider(self, spider):
        if self.email:
            # subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            message = f"{spider.name} initiated at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Opened: Email Sent to {self.to_email}")

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        if self.email:
            subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            # subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            message = f"{spider.name} Closed at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}\n\n" \
                      f"Total Item Scraped from spider={stats.get('item_scraped_count', 0)}\n"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Closed: Email Sent to {self.to_email}")
    


    ######################  Skechers  #######################################
class FilterItemPipelineSkechers(object):
    def process_item(self, item, spider):
        if 'RegularPrice' in item and item['RegularPrice']:  
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)
        
        if 'Offer' in item and item['Offer']:  
            item['Offer'] = round(float(item['Offer']), 2)

        return item
    

class UploadPipelineSkechers(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value

    def process_item(self, item, spider):
        # Send the data directly as a dictionary
        res = requests.post(
            self.api,
            json=dict(item)
        )

        if res.status_code != 200:
            LOGGER.error(f"Product Not Uploaded: {res.text}")
            if self.email:
                subject = f"{spider.name} : Product insertion has been failed due to {res.text}"
                message = f"Api Failed:" \
                          f"{res.text}\n\n\n" \
                          f"ITEM DETAILS BELOW:" \
                          f"{json.dumps(dict(item))}"

                sendemail(from_addr=from_addr,
                          to_addr_list=self.to_email,
                          cc_addr_list=["baig052@gmail.com"],
                          subject=subject,
                          message=message)
                LOGGER.error(f"Error Raised: Email Sent to {self.to_email}")

        res.raise_for_status()

        return item
    



    ######################  Adidas  #######################################
class FilterItemPipelineAdidas(object):
    def process_item(self, item, spider):
        if 'RegularPrice' in item and item['RegularPrice']:  
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)
        
        if 'Offer' in item and item['Offer']:  
            item['Offer'] = round(float(item['Offer']), 2)

        if 'RatingValue' in item and item['RatingValue']:  
            item['RatingValue'] = round(float(item['RatingValue']), 2)

        return item
    

class UploadPipelineAdidas(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value

    def process_item(self, item, spider):
        # Send the data directly as a dictionary
        res = requests.post(
            self.api,
            json=dict(item)
        )

        if res.status_code != 200:
            LOGGER.error(f"Product Not Uploaded: {res.text}")
            if self.email:
                subject = f"{spider.name} : Product insertion has been failed due to {res.text}"
                message = f"Api Failed:" \
                          f"{res.text}\n\n\n" \
                          f"ITEM DETAILS BELOW:" \
                          f"{json.dumps(dict(item))}"

                sendemail(from_addr=from_addr,
                          to_addr_list=self.to_email,
                          cc_addr_list=["baig052@gmail.com"],
                          subject=subject,
                          message=message)
                LOGGER.error(f"Error Raised: Email Sent to {self.to_email}")

        res.raise_for_status()

        return item
    



    ######################  PullBear  #######################################
class FilterItemPipelinePullBear(object):
    def process_item(self, item, spider):
        if 'Offer' in item and item['Offer']: 
            value = float(item['Offer']) / 100
            item['Offer'] = round(float(value), 2)
        
        if 'RegularPrice' in item and item['RegularPrice']:
            value = float(item['RegularPrice']) / 100  
            item['RegularPrice'] = round(float(value), 2)

        return item
    

class UploadPipelinePullBear(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value

    def process_item(self, item, spider):
        # Send the data directly as a dictionary
        res = requests.post(
            self.api,
            json=dict(item)
        )

        if res.status_code != 200:
            LOGGER.error(f"Product Not Uploaded: {res.text}")
            if self.email:
                subject = f"{spider.name} : Product insertion has been failed due to {res.text}"
                message = f"Api Failed:" \
                          f"{res.text}\n\n\n" \
                          f"ITEM DETAILS BELOW:" \
                          f"{json.dumps(dict(item))}"

                sendemail(from_addr=from_addr,
                          to_addr_list=self.to_email,
                          cc_addr_list=["baig052@gmail.com"],
                          subject=subject,
                          message=message)
                LOGGER.error(f"Error Raised: Email Sent to {self.to_email}")

        res.raise_for_status()

        return item
    


    ######################  SunAndSandSports  #######################################
class FilterItemPipelineSunAndSandSports(object):
    def process_item(self, item, spider):
        if 'Offer' in item and item['Offer']: 
            item['Offer'] = round(float(item['Offer']), 2)
        
        if 'RegularPrice' in item and item['RegularPrice']:  
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)

        if 'RatingValue' in item and item['RatingValue']:  
            item['RatingValue'] = round(float(item['RatingValue']), 2)


        if 'ProductName' in item and item['ProductName']:
            item['ProductName'] = item['ProductName'].strip()
        
        # if 'discount' in item and item['discount']:
        #     item['discount'] = item['discount'].strip()

        # if 'product_elements' in item and item['product_elements']:
        #     product_elements_str = ", ".join(item['product_elements'])
        #     item['product_elements'] = product_elements_str

        return item
    

class UploadPipelineSunAndSandSports(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value

    def process_item(self, item, spider):
        # Send the data directly as a dictionary
        res = requests.post(
            self.api,
            json=dict(item)
        )

        if res.status_code != 200:
            LOGGER.error(f"Product Not Uploaded: {res.text}")
            if self.email:
                subject = f"{spider.name} : Product insertion has been failed due to {res.text}"
                message = f"Api Failed:" \
                          f"{res.text}\n\n\n" \
                          f"ITEM DETAILS BELOW:" \
                          f"{json.dumps(dict(item))}"

                sendemail(from_addr=from_addr,
                          to_addr_list=self.to_email,
                          cc_addr_list=["baig052@gmail.com"],
                          subject=subject,
                          message=message)
                LOGGER.error(f"Error Raised: Email Sent to {self.to_email}")

        res.raise_for_status()

        return item



    ######################  Amazon  #######################################
class FilterItemPipelineAmazon(object):
    def process_item(self, item, spider):
        # Process 'Offer'
        if 'Offer' in item and item['Offer']:
            if isinstance(item['Offer'], str):  # Check if it's a string first
                value = item['Offer'].replace(',', '')
                item['Offer'] = round(float(value), 2)

        # Process 'RegularPrice'
        if 'RegularPrice' in item and item['RegularPrice']:
            if isinstance(item['RegularPrice'], str):  # Check if it's a string first
                value = item['RegularPrice'].split('AED')[1].strip()
                value = value.replace(',', '')
                item['RegularPrice'] = round(float(value), 2)

        # Process 'ProductName'
        if 'ProductName' in item and item['ProductName']:
            if isinstance(item['ProductName'], str):  # Check if it's a string first
                item['ProductName'] = item['ProductName'].strip()

        # Process 'RatingValue'
        if 'RatingValue' in item and item['RatingValue']:
            if isinstance(item['RatingValue'], str) or isinstance(item['RatingValue'], (int, float)):  # Ensure it's str or numeric
                value = str(item['RatingValue']).strip()  # Convert to string, strip spaces
                item['RatingValue'] = round(float(value), 2)

        # Process 'CategoryName'
        if 'CategoryName' in item and item['CategoryName']:
            if isinstance(item['CategoryName'], str):  # Check if it's a string first
                item['CategoryName'] = item['CategoryName'].strip()

        
        # Clean 'About' field by removing HTML tags and special characters
        if 'About' in item and item['About']:
            soup = BeautifulSoup(item['About'], 'html.parser')
            clean_about = soup.get_text(separator="\n")  # Get text with line breaks
            # Replace multiple spaces or tabs with a single space
            clean_about = re.sub(r'[ \t]+', ' ', clean_about)
            # Replace multiple newlines with a single newline
            clean_about = re.sub(r'\n+', '\n', clean_about)
            item['About'] = clean_about.strip()

        return item
    

class UploadPipelineAmazon(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value
        self.seen_items = set()

    def process_item(self, item, spider):
        item_key = item.get('SKU')
        if item_key in self.seen_items:
            LOGGER.info(f"Item already processed: {item_key}")
            return item

        self.seen_items.add(item_key)
        try:
            #LOGGER.info(f"Sending item to API: {json.dumps(dict(item))}")
            res = requests.post(self.api, json=dict(item))
            #LOGGER.info(f"API response: {res.status_code} {res.text}")
            if res.status_code != 200:
                LOGGER.error(f"Product Not Uploaded: {res.text}")
                if self.email:
                    sendemail(self.email, self.to_email, f"Product Not Uploaded: {res.text}")
                return item
            self.seen_items.remove(item_key)
        except requests.RequestException as e:
            LOGGER.error(f"Request exception: {e}")
            if self.email:
                sendemail(self.email, self.to_email, f"Request exception: {e}")
            return item
        return item

    def open_spider(self, spider):
        if self.email:
            # subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            message = f"{spider.name} initiated at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Opened: Email Sent to {self.to_email}")

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        if self.email:
            subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            # subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            message = f"{spider.name} Closed at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}\n\n" \
                      f"Total Item Scraped from spider={stats.get('item_scraped_count', 0)}\n"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Closed: Email Sent to {self.to_email}")




    ######################  Noon  #######################################
class FilterItemPipelineNoon(object):
    def process_item(self, item, spider):
        if 'Offer' in item and item['Offer']: 
            item['Offer'] = round(float(item['Offer']), 2)
        
        if 'RegularPrice' in item and item['RegularPrice']:  
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)

        if 'RatingValue' in item and item['RatingValue']:  
            item['RatingValue'] = round(float(item['RatingValue']), 2)


        if 'ProductName' in item and item['ProductName']:
            item['ProductName'] = item['ProductName'].strip()

        # Clean 'About' field by removing HTML tags and special characters
        if 'About' in item and item['About']:
            soup = BeautifulSoup(item['About'], 'html.parser')
            clean_about = soup.get_text(separator="\n")  # Get text with line breaks
            # Replace multiple spaces or tabs with a single space
            clean_about = re.sub(r'[ \t]+', ' ', clean_about)
            # Replace multiple newlines with a single newline
            clean_about = re.sub(r'\n+', '\n', clean_about)
            item['About'] = clean_about.strip()


            

        return item
    

class UploadPipelineNoon(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value
        self.seen_items = set()

    def process_item(self, item, spider):
        item_key = item.get('SKU')
        if item_key in self.seen_items:
            LOGGER.info(f"Item already processed: {item_key}")
            return item

        self.seen_items.add(item_key)
        try:
            #LOGGER.info(f"Sending item to API: {json.dumps(dict(item))}")
            res = requests.post(self.api, json=dict(item))
            #LOGGER.info(f"API response: {res.status_code} {res.text}")
            if res.status_code != 200:
                LOGGER.error(f"Product Not Uploaded: {res.text}")
                if self.email:
                    sendemail(self.email, self.to_email, f"Product Not Uploaded: {res.text}")
                return item
            self.seen_items.remove(item_key)
        except requests.RequestException as e:
            LOGGER.error(f"Request exception: {e}")
            if self.email:
                sendemail(self.email, self.to_email, f"Request exception: {e}")
            return item
        return item



    ######################  Carrefour  #######################################
class FilterItemPipelineCarrefour(object):
    def process_item(self, item, spider):
        if 'Offer' in item and item['Offer']: 
            item['Offer'] = round(float(item['Offer']), 2)
        
        if 'RegularPrice' in item and item['RegularPrice']:  
            item['RegularPrice'] = round(float(item['RegularPrice']), 2)

        if 'ModelName' in item and item['ModelName']:  
            item['ModelName'] = item['ModelName'].split(':')[-1].strip()

        # Clean 'About' field by removing HTML tags and special characters
        if 'About' in item and item['About']:
            soup = BeautifulSoup(item['About'], 'html.parser')
            clean_about = soup.get_text(separator="\n")  # Get text with line breaks
            # Replace multiple spaces or tabs with a single space
            clean_about = re.sub(r'[ \t]+', ' ', clean_about)
            # Replace multiple newlines with a single newline
            clean_about = re.sub(r'\n+', '\n', clean_about)
            item['About'] = clean_about.strip()


        return item
    

class UploadPipelineCarrefour(object):

    def __init__(self):
        self.api = '{}/api/v1/private/product/upload/'.format(HOST)
        self.email = get_project_settings().attributes['EMAIL'].value
        self.to_email = get_project_settings().attributes['TO_EMAIL'].value
        self.seen_items = set()

    def process_item(self, item, spider):
        item_key = item.get('SKU')
        if item_key in self.seen_items:
            LOGGER.info(f"Item already processed: {item_key}")
            return item

        self.seen_items.add(item_key)
        try:
            #LOGGER.info(f"Sending item to API: {json.dumps(dict(item))}")
            res = requests.post(self.api, json=dict(item))
            #LOGGER.info(f"API response: {res.status_code} {res.text}")
            if res.status_code != 200:
                LOGGER.error(f"Product Not Uploaded: {res.text}")
                if self.email:
                    sendemail(self.email, self.to_email, f"Product Not Uploaded: {res.text}")
                return item
            self.seen_items.remove(item_key)
        except requests.RequestException as e:
            LOGGER.error(f"Request exception: {e}")
            if self.email:
                sendemail(self.email, self.to_email, f"Request exception: {e}")
            return item
        return item

    def open_spider(self, spider):
        if self.email:
            # subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            subject = f"{spider.name} : Scrapper is now running from {datetime.now()}"
            message = f"{spider.name} initiated at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Opened: Email Sent to {self.to_email}")

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        if self.email:
            subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            # subject = f"{spider.name} :  Scrapper has been completed successfully at {datetime.now()}"
            message = f"{spider.name} Closed at {datetime.now()}\n" \
                      f"Check Logfile for stats for this run in \n" \
                      f"path LOGFILE={spider.custom_settings['LOG_FILE']}\n\n" \
                      f"Total Item Scraped from spider={stats.get('item_scraped_count', 0)}\n"

            sendemail(from_addr=from_addr,
                      to_addr_list=self.to_email,
                      cc_addr_list=["baig052@gmail.com"],
                      subject=subject,
                      message=message)
            LOGGER.info(f"Spider Closed: Email Sent to {self.to_email}")

