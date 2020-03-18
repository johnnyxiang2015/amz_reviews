import argparse

from amazonbot.spiders.category_multprocess import CategorySpiderMultipleProcess


def parse_args():
    parser = argparse.ArgumentParser(description='Crawler')
    parser.add_argument('-f', '--file', type=str, help='input file')

    command_args = parser.parse_args()
    return command_args


if __name__ == '__main__':
    args = parse_args()
    print(args)
    spider = CategorySpiderMultipleProcess(url_file=args.file, process_num=5)
    spider.start_requests()
