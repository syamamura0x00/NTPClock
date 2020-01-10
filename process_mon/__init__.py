
import os
import time
import queue
import logging
import threading


class ProcessMonitor(threading.Thread):
    def __init__(self, timeout=20):
        super().__init__()
        self._process_message_q = queue.Queue()
        self._timeout = timeout

    def process_message(self):
        self._process_message_q.put(1)


    def run(self):
        ts = time.time()
        while True:
            if not self._process_message_q.empty():
                _ = self._process_message_q.get()
                ts = time.time()

            if time.time() - ts > self._timeout:
                logging.critical("Process not responding")
                os._exit(1)


    def start(self):
        return super().start()
