import os

QS_DB_URI = os.environ.get('QS_DB_URI') or 'mysql+pymysql://root:123456@localhost:3307/qualys_scan'
REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
LOG_FILE = './log/qualys_scan.log'
QG_REST_URI = os.environ.get('QG_REST_URI') or 'http://localhost:2010/v1'
