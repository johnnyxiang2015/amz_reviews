from amazonbot.items import ProductItem
from lib.logger import get_logger
from lib.models import Product
from lib.utils import get_browser, get_page_content_from_url, get_product_url


class ProductSpider:
    logger = get_logger(__name__)

    def __init__(self, asin, country='US', browser=None, db=None):
        self.asin = asin
        self.country = country
        self.browser = browser if browser is not None else self.get_browser()
        if db is not None:
            db.bind([Product])

    @staticmethod
    def get_browser():
        return get_browser(profile=None)

    def start_requests(self):
        self.process(get_product_url(self.asin))

    def process(self, url_link):
        response = get_page_content_from_url(url_link, browser=self.browser)
        self.parse(response)

    def parse(self, response):
        product_item = ProductItem(asin=self.asin, html=response)
        product_item.save()


if __name__ == '__main__':
    asin = 'B00H5PJ0HW'
    ProductSpider(asin=asin, country='US').start_requests()
