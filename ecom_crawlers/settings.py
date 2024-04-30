from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
# import asyncio
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# -*- coding: utf-8 -*-

# Scrapy settings for ecom_crawlers project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'ecom_crawlers'

SPIDER_MODULES = ['ecom_crawlers.spiders']
NEWSPIDER_MODULE = 'ecom_crawlers.spiders'

# from fake_useragent import UserAgent
# ua = UserAgent()

# # Get a random browser user-agent string
# print(ua.random)
# # # Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
# USER_AGENT = ua.random

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32
# PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": False}

# DOWNLOAD_HANDLERS = {
#     "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
#     "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
# }

# TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 0.75
#DOWNLOAD_DELAY = 1.5
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 24
# CONCURRENT_REQUESTS_PER_DOMAIN = 8
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'ecom_crawlers.middlewares.EcomCrawlersSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
    
# }   
#      'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
#      'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
#     #'ecom_crawlers.middlewares.EcomCrawlersDownloaderMiddleware': 543,
# }

# DOWNLOADER_MIDDLEWARES = {
#    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
#    # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
#     'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 1,  # Lower number means higher priority
#     'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 2,
#     #'ecom_crawlers.middlewares.EcomCrawlersDownloaderMiddleware': 543,
# }
RANDOM_UA_TYPE = 'random'

DOWNLOADER_MIDDLEWARES = {
   'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
   'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   #'ecom_crawlers.pipelines.FilterItemPipelineCarrefour': 300,
    'ecom_crawlers.pipelines.UploadPipelineCarrefour': 305,

   #'ecom_crawlers.pipelines.FilterItemPipeline': 300,
    #'ecom_crawlers.pipelines.UploadPipeline': 301,

    # 'ecom_crawlers.pipelines.FilterItemPipelineAmazon': 300,
    'ecom_crawlers.pipelines.UploadPipelineAmazon': 317,

    #'ecom_crawlers.pipelines.FilterItemPipelineNoon': 300,
    'ecom_crawlers.pipelines.UploadPipelineNoon': 312,

    #'ecom_crawlers.pipelines.FilterItemPipelineJumbo': 300,
    'ecom_crawlers.pipelines.UploadPipelineJumbo': 309,

    #'ecom_crawlers.pipelines.FilterItemPipelineFirstCry': 300,
    'ecom_crawlers.pipelines.UploadPipelineFirstCry': 308,

   #'ecom_crawlers.pipelines.FilterItemPipelineHandM': 300,
    'ecom_crawlers.pipelines.UploadPipelineHandM': 316,

    #'ecom_crawlers.pipelines.FilterItemPipelineBoots': 300,
    'ecom_crawlers.pipelines.UploadPipelineBoots': 304,

    #'ecom_crawlers.pipelines.FilterItemPipelineCentrePoint': 300,
    'ecom_crawlers.pipelines.UploadPipelineCentrePoint': 306,

    #'ecom_crawlers.pipelines.FilterItemPipelineMax': 302,
    'ecom_crawlers.pipelines.UploadPipelineMax': 311,

    #'ecom_crawlers.pipelines.FilterItemPipelineEmax': 304,
    'ecom_crawlers.pipelines.UploadPipelineEmax': 307,

    #'ecom_crawlers.pipelines.FilterItemPipelineNamshi': 301,
    'ecom_crawlers.pipelines.UploadPipelineNamshi': 301,

    #'ecom_crawlers.pipelines.FilterItemPipelineLifePharmacy': 300,
    'ecom_crawlers.pipelines.UploadPipelineLifePharmacy': 310,

    #'ecom_crawlers.pipelines.FilterItemPipelineAsterPharmacy': 300,
    'ecom_crawlers.pipelines.UploadPipelineAsterPharmacy': 303,

    #'ecom_crawlers.pipelines.FilterItemPipelineSharafDG': 308,
    'ecom_crawlers.pipelines.UploadPipelineSharafDG': 314,

    #'ecom_crawlers.pipelines.FilterItemPipelineSkechers': 300,
    #'ecom_crawlers.pipelines.UploadPipelineSkechers': 301,

    #'ecom_crawlers.pipelines.FilterItemPipelineAdidas': 300,
    'ecom_crawlers.pipelines.UploadPipelineAdidas': 302,

    #'ecom_crawlers.pipelines.FilterItemPipelinePullBear': 300,
    'ecom_crawlers.pipelines.UploadPipelinePullBear': 313,

    #'ecom_crawlers.pipelines.FilterItemPipelineSunAndSandSports': 300,
    'ecom_crawlers.pipelines.UploadPipelineSunAndSandSports': 315,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False
AUTOTHROTTLE_ENABLED = True

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = False
#HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
FEED_EXPORT_ENCODING = 'utf-8'
# HOST = 'http://52.179.252.54'
HOST = 'http://127.0.0.1:8000'
CATALOGUE_URL_T = '/api/v1/private/product/get_catalogues/?vendor_name={}&short_scraper={}'
PRODUCTS_URL_T = '/api/v1/private/product/get_products/?vendor_name={}'

EMAIL = False
TO_EMAIL = ["UKSupport@datapillar.co.uk", "baig052@gmail.com"]

try:
    from .local_settings import *
except:
    pass



