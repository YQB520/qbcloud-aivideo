import logging
from decouple import config
from rq import Worker
from src.redis_queue import get_redis, get_redis_queue

if __name__ == "__main__":
    # python worker.py

    debug = config('DEBUG', default=False, cast=bool)

    if debug:
        logging.getLogger("re.worker").setLevel(logging.DEBUG)
    else:
        logging.getLogger("re.worker").setLevel(logging.ERROR)

    redis_conn = get_redis()

    queue = get_redis_queue()

    w = Worker([queue], name="video", connection=redis_conn)

    w.work()
