import logging
import time
from functools import wraps

import pymysql

logger = logging.getLogger('qualys.error')
GLOBAL_API_ERRORS = {'QAPI2000': 'Bad Login/Password'}
RECOVERABLE_API_ERROR = {'QAPI999': 'One or more IPs are not approved for this account',
                         'QAPI1905': 'parameter ip has invalid value:  (Empty IP.)'
                         }

#errors
# 'QAPI2014', 'Too many concurrent login(s)'
# 'QAPI1905', 'parameter ip has invalid value:  (Empty IP.)'
# 'QAPI1960', 'This API cannot be run again until 1 currently running instance has finished.'


def error_handling_decorator(reraise_local=False):
    """
    Decorator for handling errors,
    Args:
        reraise_local:

    Returns:



    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args):  # TODO CHECK  IF IS USED IN CORRECT CLASS
            try:
                return func(self, *args)

            except QualysApiException as e:
                logger.error('{} {} processing failed with API error ID: {} text: "{}"'.format(self.__class__.__name__, self.title, e.code, e.text))
                self._status = 'ERR_{}'.format(e.code)
                self._error_message = e.text

                # update only in case id is set
                if self._id is not None:
                    self.update()

                if e.code in GLOBAL_API_ERRORS or reraise_local:
                    raise e

            except QualysResponseException as e:
                logger.error('Response processing failed for {} {} with message: {}'.format(self.__class__.__name__, self.title, e.text))
                self._status = 'ERR_RESP'
                self.update()
                raise e

            except pymysql.err.MySQLError as e:
                if isinstance(e, (pymysql.err.IntegrityError, pymysql.err.ProgrammingError)):
                    """
                    Error related specific scan - unexpected data format, bug ...
                    Error will occur only in specific cases and is not reason to stop processing other data 
                    """
                    logger.exception('{} {} DB error during data processing occurred:'.format(self.__class__.__name__, self.title))
                    if hasattr(self, 'status'):
                        self.status = 'ERR_DB'
                    if reraise_local:
                        raise e
                else:
                    # Possibly global DB error - propagating error to outer function
                    raise e
        return wrapper
    return decorator


def error_recovery_decorator1_working(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        max_retries = 5
        for i in range(max_retries):
            try:
                return func(self, *args, **kwargs)
            except QualysApiException as e:
                if hasattr(self, '_error_handler') and e.code in self._error_handler:
                    eh_result = self._error_handler[e.code](e.text)
                    if eh_result == 'finished':  # TODO: add info about error recovery activity
                        break
                    elif eh_result == 'restart':
                        continue
                else:
                    raise e
    return wrapper


def error_recovery_decorator(max_retries=5, allowed_exceptions=()):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            i = 0
            while i < max_retries or max_retries == 0:
                i += 1
                try:
                    return func(self, *args, **kwargs)
                except allowed_exceptions as e:
                    if hasattr(self, '_error_handler') and e.code in self._error_handler:
                        eh_result = self._error_handler[e.code](e.text)
                        if eh_result == 'finished':  # TODO: add info about error recovery activity
                            break
                        elif eh_result == 'restart':
                            continue
                    else:
                        raise e
        return wrapper
    return decorator


def retry_decorator(max_retries=5, allowed_exceptions=()):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            i = 0
            exception = None
            while i <= max_retries or max_retries == 0:
                i += 1
                try:
                    return func(self, *args, **kwargs)
                except allowed_exceptions as e:
                    exception = e
                    time.sleep(5)  # TODO: change to constant
                    continue
            raise exception
        return wrapper
    return decorator


class Retry(Exception):
    """Exception raised when QualysApi response contains error code

    Attributes:
        code -- error number contained in response
        text -- text contained in response
    """

    def __init__(self, code, text='Retry exception - have to be used with retry decorator.'):
        self.code = code
        self.text = text

class QualysApiException(Exception):
    """Exception raised when QualysApi response contains error code

    Attributes:
        code -- error number contained in response
        text -- text contained in response
    """

    def __init__(self, code, text):
        self.code = code
        self.text = text

class RecoverableApiException(QualysApiException):
    """Exception raised when QualysApi response contains recoverable error code

    Attributes:
        code -- error number contained in response
        text -- text contained in response
    """

    def __init__(self, code, text):
        self.code = code
        self.text = text
        self.recoverable = True



class QualysServerException(Exception):
    """Exception raised when QualysApi response contains error code

    Attributes:
        code -- error number contained in response
        text -- text contained in response
    """

    def __init__(self, code, text):
        self.code = code
        self.text = text


class QualysResponseException(Exception):
    """Exception raised when QualysApi response contains error code

    Attributes:
        code -- error number contained in response
        text -- text contained in response
    """

    def __init__(self, code, text):
        self.code = code
        self.text = text

class ServerNotFound(Exception):
    """Exception raised when QualysApi response contains error code

    Attributes:
        code -- error number contained in response
        text -- text contained in response
    """

    def __init__(self, code, text):
        self.code = code
        self.text = text

