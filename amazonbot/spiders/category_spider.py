from bs4 import BeautifulSoup

from lib import soup_utils
from lib.constant import HTML_PARSER
from lib.logger import get_logger
from lib.models import Product
from lib.utils import get_browser, get_page_content_from_url, extract_asin_from_url

ITEM_LINK_SELECTOR = '.s-search-results .s-result-item'
NEXT_PAGE_SELECTOR = '.a-pagination .a-last a'


class CategorySpider:
    url = None
    browser = None
    logger = get_logger(__name__)

    def __init__(self, url_link, browser=None):
        self.url = url_link
        self.browser = browser if browser is not None else self.get_browser()

    @staticmethod
    def get_browser():
        #, disable_js=True, disable_image=True, headless=True
        return get_browser(profile=None)

    def start_requests(self):
        self.process(self.url)

    def process(self, url_link):
        print(url_link)
        response = get_page_content_from_url(url_link, browser=self.browser)
        self.parse(response)

    def parse(self, response):
        soup = BeautifulSoup(response, HTML_PARSER)
        items = soup_utils.find_tags(soup, ITEM_LINK_SELECTOR)
        for item in items:
            item_link = soup_utils.find_tag(item, 'a')
            asin = extract_asin_from_url(item_link['href'])
            self.save_asin(asin)

        self.process_next_page(soup)

    def process_next_page(self, soup):
        next_page = soup_utils.find_tag(soup, NEXT_PAGE_SELECTOR)
        if next_page is not None:
            next_page_url = soup_utils.format_url(next_page['href'], self.url)
            self.process(next_page_url)

    @staticmethod
    def save_asin(asin):
        try:
            product = Product()
            product.asin = asin
            product.save()
            print("%s saved" % asin)
        except:
            print("%s existed" % asin)
            pass


if __name__ == '__main__':
    url = 'https://www.amazon.com/s?i=hpc&bbn=3764441&rh=n%3A3760901%2Cn%3A3760931%2Cn%3A3764441%2Cp_85%3A2470955011%2Cp_36%3A-1000&dc&fst=as%3Aoff&qid=1584149302&rnid=386636011&ref=sr_nr_p_36_1'
    print(CategorySpider(url_link=url).start_requests())
