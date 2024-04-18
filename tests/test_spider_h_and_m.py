import unittest
from unittest.mock import MagicMock
from scrapy.http import Request, Response
from ecom_crawlers.spiders.h_and_m import HandMSpider
import json

class TestSpiderHandM(unittest.TestCase):

    def setUp(self):
        self.spider = HandMSpider()

    def test_parse(self):
    # Mocking a sample response from the API
        sample_request = Request(
            url='https://www2.hm.com/en_us/men/products/view-all/_jcr_content/main/productlisting_fa5b.display.json?sort=stock&image-size=small&image=model&offset=0&page-size=36',
            headers={'Content-Type': 'application/json'},
            meta={'main_category': 'Men', 'offset': 0, 'page': 0, 'vendor_code': 3},
            method='GET'
        )
        sample_response = Response(
            url=sample_request.url,
            request=sample_request,  # Pass the request object to associate metadata
            body=b'{"products": []}',  # Set response body directly to JSON string
            headers={'Content-Type': 'application/json'}
        )

        # body = json.loads(sample_response.body.decode('utf-8'))
        print(sample_response)
        # Call the spider's parse method with the mocked response
        parsed_items = self.spider.parse(sample_response)
        print(parsed_items)
        # Assert that the spider extracted the correct data
        #self.assertEqual(len(parsed_items), 0)



    def test_request_generation(self):
        # Ensure that the spider generates a correct request
        request = next(self.spider.start_requests())
        self.assertEqual(request.url, 'https://www2.hm.com/en_us/men/products/view-all/_jcr_content/main/productlisting_fa5b.display.json?sort=stock&image-size=small&image=model&offset=0&page-size=36')

if __name__ == '__main__':
    unittest.main()
