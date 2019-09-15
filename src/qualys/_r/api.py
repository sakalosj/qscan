import logging
import threading
from functools import wraps

import requests
from requests import RequestException

from qualys.cookies import CookieStore
from qualys.response import QualysResponse
from qualys.error import QualysApiException, error_recovery_decorator, retry_decorator
from qualys import cfg

proxy = {'https': 'http://jsakalos:45RTfgvb@globalproxy.goc.dhl.com:8080'}
headers = {'X-Requested-With': 'DHLQAPI'}
logger = logging.getLogger('qualys.api')

# def retry_decorator(max_retries=5, allowed_exceptions=()):
#     def decorator(func):
#         @wraps(func)
#         def wraper(self, *args, **kwargs):
#             i = 0
#             exception = None
#             while i < max_retries or max_retries == 0:
#                 i += 1
#                 try:
#                     return func(self, *args, **kwargs)
#                 except allowed_exceptions as e:
#                     exception = e
#                     time.sleep(5)  # TODO: change to constant
#                     continue
#                 else:
#                     raise e
#             raise exception
#         return wraper
#     return decorator



def lock_decorator(func):
    @wraps(func)
    def wraper(self, *args, **kwargs):
        with self._lock:
            return func(self, *args, **kwargs)
    return wraper





class QualysApi:
    """
    Class responsible for communication with QualysGuard using QualysGuard API
    """

    def __init__(self, qualysApiConf = None, proxyConf = None):
        """
        Initialize variables

        Args:
            qualysApiConf: QualysApi configuration
            proxyConf: proxy configuration
        """
        if (qualysApiConf or cfg.API_CONF) and (proxyConf or cfg.PROXY_CONF):
            qualysApiConf = qualysApiConf or cfg.API_CONF
            proxyConf = proxyConf or cfg.PROXY_CONF
        else:
            raise Exception('no config in paramers nor in global config')
        logger.debug('Initalizing QualysApi instance')
        self._qdomain = qualysApiConf['domain']
        self._qlogin = qualysApiConf['login']
        self._qpassword = qualysApiConf['password']
        self._connectTimeout = qualysApiConf['connectTimeout']
        self._timeout = qualysApiConf['timeout']
        self._headers = eval(qualysApiConf['headers'])
        self._proxy = qualysApiConf.getboolean('proxy')
        self._proxies = eval(qualysApiConf['proxies'])
        self._echoRequest = qualysApiConf['echoRequest']
        self._plogin = proxyConf['login']
        self._ppassword = proxyConf['passwd']
        self._purl = proxyConf['url']
        self._pport = proxyConf['port']
        self._cookieStore = CookieStore()
        self._params = {}
        self._cookie = None
        self._cookieFile = None
        self._is_logged = False
        self._lock = threading.Lock()
        # self._error_handler = {'QAPI2000': self._eh_QAPI2000_bad_login_password,
        #
        #                        }

    # @retry_decorator(max_retries=5)
    def _login(self) -> None:
        """
        Perform login to QualysGuard.

        Notes:
            Analysis of response is not required, because exception will be raised in case of
        error or login failure
        """
        apiSection = '/api/2.0/fo/session/'
        params = {
            'action': 'login',
            'username': self._qlogin,
            'password': self._qpassword
        }
        self._sendRequest(params, apiSection)
        self._is_logged = True

    def logout(self) -> None:
        """
        Perform logout of QualysGuard
        """

        apiSection = '/api/2.0/fo/session/'
        params = {
            'action': 'logout'
        }
        self.sendRequest(params, apiSection)
        self._is_logged = False

    def checkIfLogged(self) -> bool:
        """
        Checks if logged in by using simple call to QualysGuard
        Used for check if last cookie is still valid and can be used to check if QualysGuard session is still active

        Returns:
            bool: True if logged
            False if not logged

        """
        apiSection = '/api/2.0/fo/appliance/'
        param = {'action': 'list'}
        try:
            self._sendRequest(param, apiSection)
        except QualysApiException:
            return False
        else:
            return True

    def _sendRequest(self, params: dict, apiSection: str):
        """

        Args:
            params: dictionary containing api call parameters
            apiSection: api section of call

        Returns:

        """
        # TODO: ??? logic to distinguish if is logged or not so we can skip cookie check

        params['echo_request'] = self._echoRequest
        url = self._qdomain + apiSection

        # if we have available cookie file and _cookie is not set - test it
        if self._cookieStore.checkCookies() and self._cookie is None:
            self._cookie = self._cookieStore.load()

        try:
            response = requests.post(url, headers=self._headers, params=params, cookies=self._cookie)
            logger.debug('HTTP request status code: {}'.format(response.status_code))
            if response.status_code not in [401, 200]:
                raise Exception('Unable to contact qualys guard server')
            # parse response - if there will be error code QualysResponse will raise exception
            qualysResponse = QualysResponse(response.content.decode('utf-8'))  #  not using response.text because of MemorryError in case of large data
        except RequestException as e:
            logger.error('Error during requests call(http service)')
            raise e
        except QualysApiException as e:
            if e.code == 'QAPI2000' and params['action'] not in ('login', 'logout'):
                self._cookieStore.deleteCookie()
                self._login()
                raise e
            else:
                raise e

        # if it was login action store cookie and set _cookie
        if params['action'] == 'login':
            self._cookieFile = self._cookieStore.save(response.cookies)
            self._cookie = response.cookies
        return qualysResponse

    @lock_decorator
    # @retry_decorator(max_retries=1, allowed_exceptions=(QualysApiException,))
    # @error_recovery_decorator(max_retries=1, allowed_exceptions=(QualysApiException, RequestException))
    def sendRequest(self, params: dict, apiSection: str):
        """
        Function is sending login request.
        Args:
            params:
            apiSection:

        Returns:

        Notes:
            Because of login failure respond has same structure as other critical errors, error interacting decorator
            have to be applied to outer function, so it is possible to process login specific exception without
            decorator interaction or avoid lock

        """
        return self._sendRequest(params, apiSection)

