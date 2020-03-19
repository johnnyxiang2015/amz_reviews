import os
from peewee import *
from playhouse.db_url import connect
import json


def init_database():
    return connect(os.environ.get('ESDATABASE') or 'mysql://root:q1w2e3AA@146.148.80.218:3306/amazon_reviews')


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
    dimension = CharField()
    image = CharField()
    is_prime = IntegerField()
    binding = CharField()
    slug = CharField()

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
    length = DecimalField()

    description = TextField()
    upc = CharField()
    related = CharField()

    model = CharField()
    mpn = CharField()
    color = CharField()
    flavor = CharField()
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
