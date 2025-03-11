import threading
from src.utils import download_file


class DownloadThread(threading.Thread):
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue

    def run(self):
        while True:
            if not self.work_queue.empty():
                item_data = self.work_queue.get()

                download_file(item_data["path"], item_data["url"])
            else:
                break
