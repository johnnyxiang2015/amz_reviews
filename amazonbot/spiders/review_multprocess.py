import datetime
import traceback
from multiprocessing import Process, Queue, current_process

from amazonbot.spiders.review_spider import ReviewSpider
from lib.logger import get_logger
from lib.models import Product, init_database
from lib.utils import get_browser


class ReviewSpiderMultipleProcess(object):
    logger = get_logger(__name__)

    def __init__(self, process_num=5, country='US'):
        self.process_num = process_num
        self.country = country

    def worker(self, work_queue, browser, db=None):
        try:
            while True:
                if work_queue.empty():
                    print("Done %s" % current_process().name)
                    break

                product = work_queue.get()
                try:
                    ReviewSpider(asin=product.asin, browser=browser, country=self.country, db=db).start_requests()
                    product.review_last_checked = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    product.save()
                except Exception as e:
                    print(traceback.format_exc())
                    self.logger.error("%s failed  with: %s" % (current_process().name, e))
        except:
            print(traceback.format_exc())
        finally:
            pass

    def start_requests(self):

        while True:
            products = Product.select().where(Product.review_last_checked == None).limit(120)

            if len(products) == 0:
                break

            work_queue = Queue()
            processes = []

            for product in products:
                work_queue.put(product)

            for w in range(self.process_num):
                db = init_database()
                browser = get_browser(profile=None, disable_js=True, disable_image=True, headless=True)
                p = Process(target=self.worker, args=(work_queue, browser, db))
                p.start()
                processes.append([p, browser, db])

            for p in processes:
                try:
                    p[0].join()
                except (KeyboardInterrupt, SystemExit):
                    print('Exiting...Please wait!')
                    p[0].terminate()
                    p[0].join()

                p[2].close()
