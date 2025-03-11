from decouple import config
from redis import Redis
from rq import Queue

redis_host = config('REDIS_HOST', default="localhost", cast=str)

redis_post = config('REDIS_PORT', default=6379, cast=int)

# 初始化 Redis 连接（带连接池）
redis_conn = Redis(host=redis_host, port=redis_post, db=10, max_connections=20)

# 创建任务队列
task_queue = Queue("default", connection=redis_conn)


def get_redis():
    return redis_conn


def get_redis_queue():
    return task_queue
