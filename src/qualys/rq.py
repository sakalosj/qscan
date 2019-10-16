from requests import request
from rq import Queue
from redis import Redis
import time



# Tell RQ what Redis connection to use
redis_conn = Redis('redis', 6379)
redis_queue = Queue(connection=redis_conn)  # no args implies the default queue
http_redis_queue = Queue(connection=redis_conn)  # no args implies the default queue

# Delay execution of count_words_at_url('http://nvie.com')
# job = q.enqueue(test)
# print(job.result)   # => None
#
# # Now, wait a while, until the worker is finished
# time.sleep(2)
# print(job.result)   # => 889



