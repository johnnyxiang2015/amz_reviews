
from lib.utils import get_page_content_from_url



class Request(object):
    def __init__(self, url, callback=None, browser=None):
        response = get_page_content_from_url(url, browser=browser)
        callback(response)
