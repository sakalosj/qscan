from qualys import MysqlApi, QualysApi, QualysScan, QualysScanReport, QualysResponseException, QualysApiException, \
    QualysPatchReport, QualysRequest, QualysVulner, cfg, QualysServer2Req
from qualys.oat import  Oat
from dhl import Mail
import configparser
import concurrent.futures
import time
import pymysql
import logging


logger = logging.getLogger('qualys')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('log/qualys_scan.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)
config = configparser.ConfigParser()
config.read('qualys_scan.conf')
cfg.OPS_DEV_MYSQL_CONF = config['ops-dev.db']



logger = logging.getLogger('qualys.controller')
logger.setLevel(logging.DEBUG)

dbLogger = logging.getLogger('db_logger')
dbLogger.setLevel(logging.DEBUG)
fh = logging.FileHandler('log/qualys_scan_db.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
dbLogger.addHandler(fh)


consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)
dbLogger.addHandler(consoleHandler)


logger.debug('Initializing controller')
logger.debug('Reading config file')
config = configparser.ConfigParser()
config.read('qualys_scan.conf')
db = MysqlApi(config['ops-dev.db'])
qApi = QualysApi(config['qualysApiConf'], config['proxy'])
rList = {}  # :list : list of reports which are currently being processed
sList = {}  # :list : list of scans which are currently being processed


scan_conf1 = {'scan_title': 'skganws001.prg-dc.dhl.com',
             'option_title': 'API-OAT-VMS',
             'iscanner_name': 'prgdca-qua01',
             'priority': '5',
             'ip': '2.222.36.31',
             }

scan_conf2 = {'scan_title': 'skganws001.prg-dc.dhl.com',
 'option_title': 'API-OAT-VMS',
 'iscanner_name': 'prgdca-qua01',
 'priority': '5',
 'ip': '2.222.36.31',
 # 'status': 'Processed',
 # 'scan_ref': 'scan/1523517453.38417'
              }

scan_conf3 = {'scan_title': 'skganws001.prg-dc.dhl.comtest',
             'option_title': 'API-OAT-VMS',
             'iscanner_name': 'prgdca-qua01',
             'priority': '5',
             'ip': '2.222.36.31,199.40.20.75,199.40.20.76,199.40.20.77,156.137.105.12,156.137.105.11,7.16.10.69,7.252.69.46',
             }

# rawResponse = requests.post(url, headers=qApi._headers, params=params, proxies=qApi._proxies, cookies=qApi._cookie)

# def __init__(self, qualysApi: QualysApi, dbConnection: MysqlApi, initData) -> None:
# from init_test_env import *
# qApi.login()
# qReport = QualysPatchReport(qApi, db.clone(), '2.222.36.31')
# qScan = QualysScan(qApi, db.clone(), scan_conf)
# webR = QualysRequest(qApi, db.clone(), 386)
#repots: 5657554 (1)




# 199.40.20.75,199.40.20.76,199.40.20.77
#
# 156.137.105.12,156.137.105.11,7.16.10.69,7.252.69.46

# from init_test_env import *
# qApi.login()
# webR = QualysRequest(qApi, db.clone(), 390)
# webR._report = QualysPatchReport(qApi, db.clone(), None,'2.222.36.31', "title")
# webR._report.raw_data='tototototototo HURAAAAAAAAAAAAAAAAAAAA'
# webR.sendMail(webR._report)

# mail = Mail(attachment='asdddddddddddddddddddddddddd')
# mail.to = 'jan.sakalos@dhl.com'
# mail.subject = 'Qualys scan finished with status {}'.format('FFFFFFFFFFFFFF')
# mail.send()

# from init_test_env import *
#
# webR = QualysRequest(qApi, db.clone(), 390)
# webR._report = QualysPatchReport(qApi, db.clone(), None,'2.222.36.31', "title")


# from init_test_env import *
# qApi.login()
# v = QualysVulner(qApi,db.clone())
