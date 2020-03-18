import traceback
from multiprocessing import Process, Queue, current_process

from amazonbot.spiders.category_spider import CategorySpider
from lib.logger import get_logger
from lib.utils import read_csv_file


class CategorySpiderMultipleProcess(object):
    url_file = None
    process_num = 5
    work_queue = Queue()
    done_queue = Queue()
    processes = set()

    logger = get_logger(__name__)

    def __init__(self, url_file, process_num=5):
        self.url_file = url_file
        self.process_num = process_num
        self.prepare_work_queue()

    def prepare_work_queue(self):
        urls = read_csv_file(self.url_file)
        for link in urls:
            self.work_queue.put(link)

        self.process_num = min(self.process_num, len(urls))

    def worker(self):
        try:
            while not self.work_queue.empty():
                url = self.work_queue.get()
                try:
                    CategorySpider(url_link=url).start_requests()
                except Exception as e:
                    print(traceback.format_exc())
                    self.logger.error("%s failed  with: %s" % (current_process().name, e))
        except:
            print(traceback.format_exc())
        finally:
            pass


    def start_requests(self):

        for w in range(self.process_num):
            # browser = get_browser(profile=None, disable_js=True, disable_image=True, headless=True)
            p = Process(target=self.worker)
            p.start()
            self.processes.add(p)

        for p in self.processes:
            p.join()
