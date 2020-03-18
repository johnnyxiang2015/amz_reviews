from bs4 import BeautifulSoup

from amazonbot.items import ReviewItem
from lib import soup_utils
from lib.constant import HTML_PARSER
from lib.logger import get_logger
from lib.models import Review
from lib.utils import get_browser, get_page_content_from_url, get_review_url

REVIEW_SELECTOR = '#cm_cr-review_list .review'
NEXT_PAGE_SELECTOR = '.a-pagination .a-last a'


class ReviewSpider:
    logger = get_logger(__name__)
    page_processed = 0
    max_pages = 50

    def __init__(self, asin, country='US', browser=None, db=None):
        self.asin = asin
        self.country = country
        self.browser = browser if browser is not None else self.get_browser()
        if db is not None:
            db.bind([Review])

    @staticmethod
    def get_browser():
        return get_browser(profile=None)

    def start_requests(self):
        self.process(get_review_url(self.asin))

    def process(self, url_link):
        print(url_link)
        response = get_page_content_from_url(url_link, browser=self.browser)
        self.parse(response)

    def parse(self, response):
        soup = BeautifulSoup(response, HTML_PARSER)
        item_tags = soup_utils.find_tags(soup, REVIEW_SELECTOR)
        for item_tag in item_tags:
            review_item = ReviewItem(asin=self.asin, item_html=item_tag)
            print(review_item)
            review_item.save()

        self.process_next_page(soup)

    def process_next_page(self, soup):
        self.page_processed += 1
        if self.page_processed > self.max_pages:
            return

        next_page = soup_utils.find_tag(soup, NEXT_PAGE_SELECTOR)
        if next_page is not None:
            next_page_url = soup_utils.format_url(next_page['href'], get_review_url(self.asin, self.country))
            self.process(next_page_url)


if __name__ == '__main__':
    asin = 'B007L0DPE0'
    ReviewSpider(asin='B007L0DPE0', country='US').start_requests()
