# Gobazzar Crawlers Platform

### Local Machine Deployment Setup

#### Database setup
Please make sure you have working mysql installed.
* Create database provide Database credentials to developer

#### Python Setup
Python 3.6+ should be installed

#### Code setup 
Please ensure you have working **Python 3.6+**

* ``git@github.com:abdullahbaig052/gobazzar_crawlers.git``
* ``cd gobazzar_crawlers && virtualenv -p python3 envname``
* ``source envname/bin/activate``

Installing project packages in Virtualenv created for GoBazzar
* ``pip install -r requirements.txt``
* ``cd ecom_api && python manage.py migrate``

Setup your User to use admin panel:
* ``Python manage.py createsuperuser`` 
And test by login at http://domain.com/admin

Running Django Server
* ``Python manage.py runserver`` 

It stays running in one terminal.
Open another terminal & run below command.
* ``cd gobazzar_crawlers``

scrapy.cfg can be seen before running this command
* ``scrapy crawl noon``

Incase want in order to maintain queue service:
* ``scrapy crawl noon -s JOBDIR=crawls/noon-v(n)``

Tools Used:
* `Scrapy` in order to scrape data from website
* `Django` web app framework
* `rest_framework` Django Api framework used for validation and insertion of data scraped via scrapper
* `MySQL` Database


### For deployment of django app - helping material:
 Nginx is a reverse proxy for Gunicorn. Gunicorn serves your flask app and Nging sits in front of it and decides where a request should go. For example, if the incoming request is an http request Nginx redirects it to gunicorn, if it is for a static file, it serves it itself. Read more about how to use Nginx ang Gunicorn and how to deploy them starting from here: 
 
 `http://rahmonov.me/posts/run-a-django-app-with-gunicorn-in-ubuntu-16-04/`
### For Scrapy spider deployment - helping material:
You follow below link 

`https://towardsdatascience.com/a-minimalist-end-to-end-scrapy-tutorial-part-iv-3290d76a2aef`
 
 ### Notes:
 * Product gets validate `/insert/update` into the db on each product link once scraped.
 * Log files can be seen under `/scrapy-logs` on datetime of scraper run.
 * `-s JOBDIR=crawls/noon-v(n)` this argument should be used and should have unique `n` number in order to pause/resume the scraper.
 * `-a short_scraper=True` this argument should be used in order to run short_scraper
 
 ## Requirements:
 ### For proxy: 
 *Please review this article. We will be adding provided proxy link in scraper's each request `meta` key
 `https://blog.scrapinghub.com/scrapy-proxy`
 
 ### For Email:
  if you have any smtp already configured you can provide me below details. i.e: for gmail smtp this is the template
 * `EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'`
 * `EMAIL_USE_TLS = True`
 * `EMAIL_HOST = 'smtp.gmail.com'`
 * `EMAIL_HOST_USER = 'youremail@gmail.com'`
 * `EMAIL_HOST_PASSWORD = 'email_password'`
 * `EMAIL_PORT = 587`
 
 