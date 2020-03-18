import platform
import re
import time
import traceback
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException

from lib.constant import *
from lib.logger import get_logger

logger = get_logger(__name__)

_extract_asin_regexp = re.compile(r'(/dp/|/product-reviews/|/gp/product/)(?P<asin>[^/]+)/?')

profile_dir = APP_ROOT_DIR + "/web_profile"

if os.path.isdir(profile_dir) is False:
    os.makedirs(profile_dir)

chromedriver_version = 77
MAX_DRIVER_VERSION = 81


class RobotCheckException(Exception):
    pass


def get_browser(profile='Profile 1', headless=False, disable_image=False, disable_js=False):
    global chromedriver_version
    options = webdriver.ChromeOptions()

    if platform.system() == "Windows":
        browser = webdriver.Chrome(APP_ROOT_DIR + "/driver/chromedriver")
        options.add_argument('--disable-gpu')  # Last I checked this was necessary.
    else:
        if platform.system().lower() == "linux":
            driver_path = APP_ROOT_DIR + "/driver/chromedriver_linux_%s" % chromedriver_version
            os.chmod(driver_path, 0o777)
            options.add_argument("--no-sandbox");
            options.add_argument("--disable-dev-shm-usage");
        else:
            driver_path = APP_ROOT_DIR + "/driver/chromedriver_mac"

        if profile is not None:
            options.add_argument("user-data-dir=" + profile_dir)
            options.add_argument('--profile-directory=Profile 1')

        if headless:
            options.add_argument('--headless')
            options.headless = True
        prefs = {}
        if disable_image:
            prefs.update({"profile.managed_default_content_settings.images": 2})

        if disable_js:
            prefs.update({'profile.managed_default_content_settings.javascript': 2})

        if len(prefs) > 0:
            options.add_experimental_option("prefs", prefs)

        try:
            browser = webdriver.Chrome(chrome_options=options, executable_path=driver_path)
        except SessionNotCreatedException as e:
            if chromedriver_version > MAX_DRIVER_VERSION:
                raise e

            chromedriver_version = chromedriver_version + 1
            return get_browser(profile=profile, headless=headless, disable_image=disable_image, disable_js=disable_js)

    return browser


def get_page_content_from_url(url, browser, try_times=3):
    # print url
    for x in range(try_times):
        try:
            browser.get(url)
            html_source = browser.page_source
            if "robot" in html_source and "captcha" in html_source:
                raise RobotCheckException()
            return html_source
        except RobotCheckException:
            logger.error("Robot check for %s" % url)
            time.sleep(60)
        except ConnectionRefusedError:
            logger.error("Connection refused for %s" % url)
            time.sleep(2)
            # print(traceback.format_exc())

    return None


def extract_asin_from_url(url):
    match = _extract_asin_regexp.search(url)
    if match is None:
        return None
    return str(match.group('asin'))


def fix_input_file(file_path):
    if file_path is None:
        raise FileExistsError("input file is required.")

    if file_path[-3:].lower() != 'csv':
        file_path = file_path + '.csv'

    if not os.path.exists(file_path):
        file_path = APP_ROOT_DIR + '/links/' + file_path

    if not os.path.exists(file_path):
        raise FileExistsError('File %s not existed' % file_path)

    return file_path


def read_csv_file(filename):
    file_path = fix_input_file(filename)
    with open(file_path) as f:
        lines = [line.strip() for line in f.readlines() if len(line.strip()) > 0]
        return lines


def get_sales_channel(region):
    region = region.upper()
    return SALES_CHANNELS[region] if region in SALES_CHANNELS else None


def get_product_url(asin, country='US'):
    return 'https://www.%s/dp/%s' % (get_sales_channel(country), asin)


def get_review_url(asin, country='US'):
    return 'https://www.%s/product-reviews/%s/ref=cm_cr_arp_d_viewopt_srt?reviewerType=avp_only_reviews&pageNumber=1&sortBy=recent' % (
    get_sales_channel(country), asin)
