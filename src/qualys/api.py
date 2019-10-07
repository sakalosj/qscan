from session_pool import session_pool

from hlp.const import methods


class Api:
    def __init__(self, section, base_url='http://localhost:5000/api/v1.0'):
        self.base_url = base_url
        self.section = section

    @property
    def url(self):
        return '/'.join([self.base_url, self.section])

    def get(self, id=None):
        method = methods.GET

        response = session_pool.send_task(method, '/'.join(filter(None, [self.url, str(id)])))
        return response.json()

    def post(self, json_data):
        method = methods.POST
        options = {'json': json_data}

        response = session_pool.send_task(method, self.url, options)
        return response.json()
