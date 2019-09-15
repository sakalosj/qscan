import logging

from abc import ABC, abstractmethod
from qualys.api import QualysApi
# from qualys.db import MysqlApi
from qualys import cfg


logger = logging.getLogger('qualys.qualys_item')

# class QualysGuardItem(ABC):
#     pass

class QualysBaseItem(ABC):
    # _class_db_connecttion_ =  MysqlApi()

    def __init__(self, mysqlApi=None, db_conf=None):
        super().__init__()
        if mysqlApi is None:
            self._mysqlApi = MysqlApi(db_conf=db_conf)

class QualysScanItemABC(ABC):
    def __init__(self, init_data = None, qualysApi=None, mysqlApi=None, *args, **kwargs):
        super().__init__()

    @property
    def error_message(self):
        return self._error_message

    # @abstractmethod
    @error_message.setter
    def error_message(self, error):
        # TODO: update db error message
        self._error_message = error
        # raise NotImplementedError

    @abstractmethod
    def update(self):
        # raise NotImplementedError
        pass

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if self._status != status:
            logger.debug('Setting scan instance {} status to {} and updating DB'.format(self.title, status))
            self._status = status
            self.update()


class QuakyReport(QualysScanItemABC):
    @classmethod
    def get_server_vulner(self, server, report_id = None):

        with self._db_connection.get_cursor() as cursor:
            sql = '''SELECT DISTINCT qv.* FROM server AS s
                JOIN  request_server2vulner AS s2v
                ON s.ip = s2v.request2server_server_ip_fk AND s.last_report = s2v.qreport2server_qreport_id_fk
                JOIN vulner AS v 
                ON v._qid = s2v.vulner_qid_fk
                WHERE s.ip = %s
            '''
            values = server.ip
            cursor.execute(sql, values)
            self._db_connection.commit()
            vulner_list = cursor.fetchall()
        return vulner_list

    @classmethod
    def get_server_status(self, server, report_id = None):

        with self._db_connection.get_cursor() as cursor:
            sql = '''SELECT DISTINCT r2s.* FROM server AS s
                JOIN  request2server AS r2s
                ON s.ip = r2s.server_ip_fk and s.last_report = r2s.request_id_fk
                WHERE qs.ip = %s
            '''
            values = server.ip
            cursor.execute(sql, values)
            self._db_connection.commit()
            result = cursor.fetchone()
        return result['status']
