import time

from requests import request

from hlp.cfg import QG_REST_URI
from hlp.const import methods, status, stat


class Api:
    def __init__(self, section, base_url=QG_REST_URI, sleep_time=3, timeout=300):
        self.base_url = base_url
        self.section = section
        self.sleep_time = sleep_time
        self.run_timeout = timeout

    @property
    def url(self):
        return '/'.join([self.base_url, self.section])

    def _request(self, method, url, **kwargs):
        response = request(method, url, **kwargs)
        if response.status_code > 399:
            raise Exception('http status code: {}'.format(response.status_code))
        json_data = response.json()
        return json_data

    def _request_status_check(self, method, url, **kwargs):
        start_time = time.time()
        while True:
            json_data = self._request(method, url, **kwargs)

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
