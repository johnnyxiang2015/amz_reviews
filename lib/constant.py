import os

APP_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

HTML_PARSER = 'html.parser'
LXML_PARSER = 'lxml'
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

MARKETPLACE_IDS = {
    "US": "ATVPDKIKX0DER",
    "CA": "A2EUQ1WTGCTBG2",
    "MX": "A1AM78C64UM0Y8",
    "UK": "A1F83G8C2ARO7P",
    "DE": "A1PA6795UKMFR9",
    "ES": "A1RKKUPIHCS9HS",
    "FR": "A13V1IB3VIYZZH",
    "IT": "APJ6JRA9NG5V4",
    "JP": "A1VC38T7YXB528",
    "AU": "A39IBJ37TRP1C6",
    "CN": "AAHKV2X7AFYLW"
}
SALES_CHANNELS = {
    "US": "Amazon.com",
    "CA": "Amazon.ca",
    "MX": "Amazon.com.au",
    "UK": "Amazon.co.uk",
    "DE": "Amazon.de",
    "ES": "Amazon.es",
    "FR": "Amazon.fr",
    "IT": "Amazon.it",
    "JP": "Amazon.com.jp",
    "AU": "Amazon.com.au",
    "CN": "Amazon.cn"
}
