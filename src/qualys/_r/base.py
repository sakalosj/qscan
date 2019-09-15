from qualys.api import QualysApi
from qualys.db import MysqlApi



class QualysBase:
    def __init__(self, qualysApi: QualysApi, dbConnection: MysqlApi, initData):
        self._qualysApi = qualysApi
        self._dbConnection = dbConnection


