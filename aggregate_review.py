import argparse
import traceback

import sys

from lib.models import esdb, Aggregated, Product, Review

SCORE_MATRIX = {
    1: -8,
    2: -5,
    3: -1,
    4: 3,
    5: 5
}


def init_model(asin):
    try:
        ar = Aggregated.get(Aggregated.asin == asin)
    except:
        ar = Aggregated()
        ar.asin = asin
        ar.total = 0
        ar.average = 0
        ar.score = 0
        ar.total_1 = 0
        ar.total_2 = 0
        ar.total_3 = 0
        ar.total_4 = 0
        ar.total_5 = 0
        ar.total_helpful = 0
        ar.total_score = 0

        product = Product.get(Product.asin == asin)
        ar.sales_rank = product.sales_rank

    if ar.sales_rank is None:
        ar.sales_rank = 0

    return ar


def adjust_avg(aggregated, rating):
    return (float(aggregated.average) * float(aggregated.total) + float(rating)) / float(aggregated.total + 1)


def adjust_score(aggregated, review):
    return (float(aggregated.score) * float(
        aggregated.total_helpful * 0.3 + aggregated.total) + float(
        review.rating * (1 + review.helpful * 0.3))) / float(
        (aggregated.total_helpful + review.helpful) * 0.3 + aggregated.total + 1)


def adjust_total(aggregated, review):
    return aggregated.total_score + (1 + review.helpful * 0.3) * SCORE_MATRIX[review.rating]


def adjust_rating(aggregated, review):
    if review.rating == 1:
        aggregated.total_1 = aggregated.total_1 + 1
    elif review.rating == 2:
        aggregated.total_2 = aggregated.total_2 + 1
    elif review.rating == 3:
        aggregated.total_3 = aggregated.total_3 + 1
    elif review.rating == 4:
        aggregated.total_4 = aggregated.total_4 + 1
    elif review.rating == 5:
        aggregated.total_5 = aggregated.total_5 + 1

    return aggregated


def aggregate_reviews_by_asin(asin):
    aggregated = init_model(asin)

    reviews = Review.select().where(Review.asin == asin, Review.aggregated == 0)

    for review in reviews:
        aggregated.average = adjust_avg(aggregated, review.rating)
        aggregated.score = adjust_score(aggregated, review)
        aggregated.total_score = adjust_total(aggregated, review)
        aggregated.total_helpful = aggregated.total_helpful + review.helpful
        aggregated.total = aggregated.total + 1
        aggregated = adjust_rating(aggregated, review)

        if aggregated.total % 10 == 1:
            print(aggregated.total, aggregated.average, aggregated.score,
                  aggregated.total_score)

    aggregated.save()

    query = Review.update(aggregated=1).where(Review.asin == asin)
    query.execute()


def parse_args():
    parser = argparse.ArgumentParser(description='Crawler')
    parser.add_argument('-l', '--limit', type=int, default=0, help='max process')
    command_args = parser.parse_args()
    return command_args


if __name__ == '__main__':
    args = parse_args()
    limit = args.limit

    page_limit = 1000 if limit == 0 or limit > 1000 else limit

    total_processed = 0
    while True:
        sql = 'select distinct asin from reviews where aggregated = 0 order by id asc  limit %s'
        cursor = esdb.execute_sql(sql, [page_limit])
        rows = cursor.fetchall()
        if len(rows) == 0:
            break

        for row in rows:
            try:
                aggregate_reviews_by_asin(row[0])
            except:
                print(traceback.format_exc())

            total_processed += 1
            if total_processed > limit > 0:
                sys.exit(0)
