import datetime
import json
import re

from bs4 import BeautifulSoup
from peewee import DoesNotExist

from lib import soup_utils
from lib.constant import HTML_PARSER
from lib.models import Review


class ReviewItem(object):
    REVIEW_RATING_SELECTOR = '.a-icon.a-icon-star.review-rating'
    REVIEW_TITLE_SELECTOR = 'a.a-size-base.a-link-normal.review-title'
    REVIEW_AUTHOR_SELECTOR = 'span.a-profile-name'
    REVIEW_DATE_SELECTOR = 'span.review-date'
    REVIEW_CONTENT_SELECTOR = '.a-size-base.review-text'
    REVIEW_VOTES_SELECTOR = '.review-votes'

    def __init__(self, asin, item_html):
        self.item_soup = BeautifulSoup(item_html, HTML_PARSER) if isinstance(item_html, str) else item_html

        self.asin = asin
        self.review_id = self.item_soup["id"]
        self.rating = self.parse_rating()
        self.title = self.parse_title()
        self.author = self.parse_author()
        self.date_created = self.parse_date()
        self.content = self.parse_content()
        self.helpful = self.parse_helpful()

    def parse_rating(self):
        try:
            stars_text = soup_utils.find_tag(self.item_soup, ReviewItem.REVIEW_RATING_SELECTOR).text.replace(
                "out of 5 stars",
                "").strip()
            return int(float(stars_text))
        except:
            return 0

    def parse_title(self):
        try:
            return soup_utils.find_tag(self.item_soup, ReviewItem.REVIEW_TITLE_SELECTOR).text.strip()
        except:
            return None

    def parse_author(self):
        try:
            return soup_utils.find_tag(self.item_soup, ReviewItem.REVIEW_AUTHOR_SELECTOR).text.strip()
        except:
            return None

    def parse_date(self):
        try:
            date_text = soup_utils.find_tag(self.item_soup, ReviewItem.REVIEW_DATE_SELECTOR).text
            date_text = date_text.split('on')[-1].strip()
            return datetime.datetime.strptime(date_text, '%B %d, %Y')
        except:
            return None

    def parse_content(self):
        try:
            return soup_utils.find_tag(self.item_soup, ReviewItem.REVIEW_CONTENT_SELECTOR).decode_contents(
                formatter="html").strip()
        except:
            return None

    def parse_helpful(self):
        try:
            vote_text = soup_utils.find_tag(self.item_soup, ReviewItem.REVIEW_VOTES_SELECTOR).text
            return vote_text.replace("people found this helpful.", "").strip()
        except:
            return 0

    def save(self):
        try:
            Review.get(Review.review_id == self.review_id)
            return
        except DoesNotExist:
            review = Review()
            review.review_id = self.review_id

        review.asin = self.asin
        review.rating = self.rating
        review.title = self.title
        review.author = self.author
        review.date_created = self.date_created
        review.content = self.content
        review.helpful = self.helpful

        review.save()

    def __str__(self):
        return json.dumps({
            'review_id': self.review_id,
            'asin': self.asin,
            'rating': self.rating,
            'title': self.title,
            'author': self.author,
            'date_created': self.date_created,
            'content': self.content,
            'helpful': self.helpful
        }, default=str)


class ProductItem(object):
    TITLE_SELECTOR = '#productTitle'
    BRAND_SELECTOR = '#bylineInfo'
    PRICE_SELECTOR = '#priceblock_ourprice'
    FEATURE_BULLETS_SELECTOR = '#feature-bullets'
    BREADCRUMBS_SELECTOR = '#wayfinding-breadcrumbs_feature_div'
    DESCRIPTION_SELECTOR = '#productDescription'
    IMPORTANT_INFO_SELECTOR = '#importantInformation'
    DETAIL_BULLETS_SELECTOR = '#detail-bullets li'

    def __init__(self, html):
        self.soup = BeautifulSoup(html, HTML_PARSER)

        self.name = self.parse_name()
        self.slug = self.create_slug()

        self.brand = self.parse_brand()
        self.price = self.parse_price()
        self.feature_list = self.parse_feature_list()
        self.descriptions = self.parse_description()
        self.categories = self.parse_breadcrumbs()
        details = self.parse_detail()
        self.dimensions = details['dimensions'] if 'dimensions' in details else None
        self.upc = details['upc'] if 'upc' in details else None
        self.mpn = details['mpn'] if 'mpn' in details else None

    def parse_name(self):
        return soup_utils.find_tag(self.soup, self.TITLE_SELECTOR).text.strip()

    def parse_brand(self):
        return soup_utils.find_tag(self.soup, self.BRAND_SELECTOR).text.strip()

    def parse_price(self):
        price_text = soup_utils.find_tag(self.soup, self.PRICE_SELECTOR).text.strip()
        price_text = re.sub(r'[^0-9.,\-]', '', price_text)
        return round(float(price_text), 2)

    def parse_feature_list(self):
        try:
            return soup_utils.find_tag(self.soup, self.FEATURE_BULLETS_SELECTOR).decode_contents(
                formatter="html").strip()
        except:
            return None

    def parse_description(self):
        try:
            return soup_utils.find_tag(self.soup, self.DESCRIPTION_SELECTOR).decode_contents(
                formatter="html").strip()
        except:
            return None

    def parse_detail(self):
        detail_bullets = soup_utils.find_tags(self.soup, self.DETAIL_BULLETS_SELECTOR)
        details = dict()
        for bullet in detail_bullets:
            text = bullet.text
            parts = [t.strip() for t in text.split(":")]
            if len(parts) < 2:
                continue
            key = parts[0]
            value = parts[1]
            if 'Product Dimensions' == key:
                details['dimensions'] = value
            if 'UPC' == key:
                details['upc'] = value
            if 'Item model number' == key:
                details['mpn'] = value

        return details

    def parse_breadcrumbs(self):
        return soup_utils.find_tag(self.soup, self.BREADCRUMBS_SELECTOR).text.strip()

    def create_slug(self):
        # print text
        t = self.name.replace(" ", "-").strip().lower()
        t = t.replace("&", "-")
        t = re.sub(r'[^a-z0-9\-]', '', t)

        while "--" in t:
            t = t.replace("--", "-")

        return t

    def save(self):
        pass

    def __str__(self):
        r = {}
        for k in self.__dict__.keys():
            if not k.startswith('_') and k not in ['soup']:
                try:
                    r[k] = str(getattr(self, k))
                except:
                    r[k] = json.dumps(getattr(self, k))

        return str(r)