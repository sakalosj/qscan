from qualys import error
import logging



def apiErrorDecorator(func):
    def wrapper(self,*args):
        try:
            return func(self,*args)
        except error.QualysApiException as e:
            print('apidecorator')
            self._status='API_ERROR'
            raise e
    return wrapper




