import os
from peewee import *
from playhouse.db_url import connect
import json

from playhouse.pool import PooledMySQLDatabase


# esdb = connect(os.environ.get('ESDATABASE') or 'mysql://root:q1w2e3AA@146.148.80.218:3306/amazon_reviews')
#

def init_database():
    db = PooledMySQLDatabase(
        "amazon_reviews", user="root", host="146.148.80.218", port=3306, password="q1w2e3AA",
        max_connections=8, stale_timeout=300)
    return db


esdb = init_database()


class ESBaseModel(Model):
    def __str__(self):
        r = {}
        for k in self._data.keys():
            try:
                r[k] = str(getattr(self, k))
            except:
                r[k] = json.dumps(getattr(self, k))
        return str(r)

    class Meta:
        database = esdb


class Product(ESBaseModel):
    asin = CharField()
    name = CharField()
    brand = CharField()
    price = DecimalField()
    review_last_checked = DateTimeField()

    sales_rank = IntegerField()

    categories = TextField()

    weight = CharField()
    dimension = CharField()
    size = CharField()
    packageqty = CharField()
    image = CharField()
    is_prime = IntegerField()
    binding = CharField()

    width = DecimalField()
    height = DecimalField()
    length = DecimalField()
    slug = CharField()

    description = TextField()
    upc = CharField()
    related = CharField()

    class Meta:
        db_table = 'products'


class ProductInfo(ESBaseModel):
    asin = CharField()
    all_info = TextField()
    description = TextField()

    class Meta:
        db_table = 'more_info'


class ProductAttr(ESBaseModel):
    asin = CharField()
    categories = TextField()

    weight = CharField()
    dimensions = CharField()
    size = CharField()
    images = TextField()
    binding = CharField()

    width = DecimalField()
    height = DecimalField()
    depth = DecimalField()

    description = TextField()
    upc = CharField()
    related = CharField()

    model = CharField()
    mpn = CharField()
    color = CharField()
    parent_asin = CharField()
    features = TextField()
    manufacturer = CharField()
    publisher = CharField()

    class Meta:
        db_table = 'product_attrs'


class Category(ESBaseModel):
    id = PrimaryKeyField()
    name = CharField()
    slug = CharField()
    _lft = IntegerField()
    _rgt = IntegerField()
    parent_id = IntegerField()

    class Meta:
        db_table = 'categories'


class CategoryProduct(ESBaseModel):
    category_id = IntegerField()
    asin = CharField()

    class Meta:
        db_table = 'category_products'


class Review(ESBaseModel):
    review_id = CharField()
    asin = CharField()
    title = CharField()
    content = TextField()
    author = CharField()
    date_created = DateField()
    rating = IntegerField()
    helpful = IntegerField()
    not_helpful = IntegerField()
    aggregated = IntegerField()

    class Meta:
        db_table = 'reviews'


class Aggregated(ESBaseModel):
    asin = CharField()
    total = IntegerField()
    total_1 = IntegerField()
    total_2 = IntegerField()
    total_3 = IntegerField()
    total_4 = IntegerField()
    total_5 = IntegerField()
    total_helpful = IntegerField()
    last_updated = DateTimeField()

    score = DecimalField()
    average = DecimalField()

    total_score = IntegerField()

    most_used_words = CharField()
    most_positive_words = CharField()
    most_negative_words = CharField()
    positive_summary = TextField()
    negative_summary = TextField()

    sales_rank = IntegerField()
    adjusted_score = DecimalField()
    pos_features = IntegerField()
    neg_features = IntegerField()

    class Meta:
        db_table = 'reviews_aggregated'


class ProductFeature(ESBaseModel):
    asin = CharField()
    feature = CharField()
    neg = IntegerField()
    pos = IntegerField()
    pos_summary = TextField()
    neg_summary = TextField()

    class Meta:
        db_table = 'product_features'