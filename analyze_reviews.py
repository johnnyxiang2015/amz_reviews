import argparse
import traceback

import sys

from lib.models import esdb
from lib.nlp import review_top_keywords_by_asin


def parse_args():
    parser = argparse.ArgumentParser(description='Crawler')
    parser.add_argument('-l', '--limit', type=int, default=1, help='max process')
    command_args = parser.parse_args()
    return command_args


if __name__ == '__main__':

    args = parse_args()
    limit = args.limit
    page_limit = limit if 0 < limit < 1000 else 1000

    total_processed = 0
    while True:
        sql = "select distinct asin from reviews_aggregated where positive_summary is null  order by id asc limit %s"
        print(sql)
        cursor = esdb.execute_sql(sql, [page_limit])
        rows = cursor.fetchall()

        for row in rows:
            try:
                review_top_keywords_by_asin(row[0])
            except:
                print(traceback.format_exc())
            total_processed += 1
            if total_processed >= limit:
                sys.exit(0)
