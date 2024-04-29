from scrapy.utils.log import configure_logging
from twisted.internet import reactor, defer

from scrapy.utils.project import get_project_settings
from ecom_crawlers.spiders.adidas_uae import AdidasSpider
from ecom_crawlers.spiders.amazon_new import AmazonSpider
from ecom_crawlers.spiders.asterpharmacy_web import AsterPharmacySpider
from ecom_crawlers.spiders.boots import BootsSpider
from ecom_crawlers.spiders.carrefour import CarreFourSpider
from ecom_crawlers.spiders.centrepoint_updated import CentrePointSpider
from ecom_crawlers.spiders.emax import EmaxSpider
from ecom_crawlers.spiders.firstcry import FirstCrySpider
from ecom_crawlers.spiders.jumbo import JumboSpider
from ecom_crawlers.spiders.namshi import NamshiSpider
from ecom_crawlers.spiders.h_and_m_updated import HandMSpider
from ecom_crawlers.spiders.lifepharmacy import LifePharmacySpider
from ecom_crawlers.spiders.max import MaxSpider
from ecom_crawlers.spiders.noon_new import NoonSpider
from ecom_crawlers.spiders.pullbear import PullBearSpider
from ecom_crawlers.spiders.sharafdg import SharafDGSpider
from ecom_crawlers.spiders.sssports import SunAndSandSportsSpider
from scrapy.crawler import CrawlerRunner
import os
import logging
from datetime import datetime


def main():
    # Step 1: Ensure the directory for logs exists
    log_dir = 'scrapy-logs'
    os.makedirs(log_dir, exist_ok=True)

    # Step 2: Configure logging
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"scrapy_{timestamp}.log"
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename=os.path.join(log_dir, log_filename),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Additional logging for debugging
    logger = logging.getLogger(__name__)
    logger.info("Starting the main function")

    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    
    @defer.inlineCallbacks
    def crawl():
        yield runner.crawl(NamshiSpider)
        yield runner.crawl(AdidasSpider)
        yield runner.crawl(AsterPharmacySpider)
        yield runner.crawl(BootsSpider)
        yield runner.crawl(CarreFourSpider)
        yield runner.crawl(CentrePointSpider)
        yield runner.crawl(EmaxSpider)
        yield runner.crawl(FirstCrySpider)
        yield runner.crawl(JumboSpider)
        yield runner.crawl(LifePharmacySpider)
        yield runner.crawl(MaxSpider)
        yield runner.crawl(NoonSpider)
        yield runner.crawl(PullBearSpider)
        yield runner.crawl(SharafDGSpider)
        yield runner.crawl(SunAndSandSportsSpider)
        yield runner.crawl(HandMSpider)
        yield runner.crawl(AmazonSpider)
        reactor.stop()

    crawl()

    logger.info("Starting the reactor")
    reactor.run()  # the script will block here until all crawling jobs are finished
    logger.info("Reactor stopped")


if __name__ == '__main__':
    main()


