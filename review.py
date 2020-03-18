import argparse

from amazonbot.spiders.category_multprocess import CategorySpiderMultipleProcess
from amazonbot.spiders.review_multprocess import ReviewSpiderMultipleProcess


def parse_args():
    parser = argparse.ArgumentParser(description='Crawler')
    parser.add_argument('-c', '--country', type=str, default='us', help='sales channel')
    parser.add_argument('-p', '--process_num', type=int, default=8, help='max process')
    command_args = parser.parse_args()
    return command_args


if __name__ == '__main__':
    args = parse_args()
    print(args)
    spider = ReviewSpiderMultipleProcess(process_num=args.process_num, country=args.country)
    spider.start_requests()
