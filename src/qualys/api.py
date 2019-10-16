import time

from requests import request
from session_pool import session_pool

from hlp.const import methods, status, stat


# def process_request(method, url, redis_queue=http_rq):
#     job = redis_queue.enqueue(request, method, url)
#
#     while True:
#         if job.is_finished:
#             return job.result.json()
#         if job.is_failed:
#             raise Exception('HTTP job failed')
#
#
# class Api:
#     def __init__(self, section, base_url='http://localhost:5000/api/v1.0'):
#         self.base_url = base_url
#         self.section = section
#
#     @property
#     def url(self):
#         return '/'.join([self.base_url, self.section])
#
#     def get(self, id=None):
#         method = methods.GET
#
#         response = session_pool.send_task(method, '/'.join(filter(None, [self.url, str(id)])))
#         return response.json()
#
#     def post(self, json_data):
#         method = methods.POST
#         options = {'json': json_data}
#
#         response = session_pool.send_task(method, self.url, options)
#         return response.json()
#

class Api:
    def __init__(self, section, base_url='http://localhost:2010/v1', sleep_time=3, timeout=300):
        self.base_url = base_url
        self.section = section
        self.sleep_time = sleep_time
        self.run_timeout = timeout

    @property
    def url(self):
        return '/'.join([self.base_url, self.section])

    def _request(self, method, url, **kwargs):
        response = request(method, url, **kwargs)
        json_data = response.json()
        return json_data

    def _request_status_check(self, method, url, **kwargs):
        start_time = time.time()
        while True:
            response = request(method, url, **kwargs)
            json_data = response.json()
            if json_data['status'] in [stat.FINISHED, stat.FAILED]:
                break
            if (time.time() - start_time) > self.run_timeout:
                raise TimeoutError
            time.sleep(self.sleep_time)
        return json_data

    def get(self, id, check_status=False):
        request_fn = self._request_status_check if check_status else self._request

        if not isinstance(id, int):
            raise ValueError('id have to be int, {} provided'.format(id))
        method = methods.GET
        str_id = '' if id is None else str(id)
        url = '/'.join(filter(None, [self.url, str_id]))

        return request_fn(method, url)

    def post(self, json_data):
        method = methods.POST
        options = {'json': json_data}

        return self._request(method, self.url, **options)
