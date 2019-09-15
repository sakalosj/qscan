import concurrent
import datetime
from collections import defaultdict
import logging
from concurrent.futures.thread import ThreadPoolExecutor as thr_pool

from sqlalchemy import and_, Column, Integer, String, orm
from sqlalchemy.ext.associationproxy import association_proxy

from hlp.const import status
from qualys.association_tables import Request2Server
from . import Base, BaseMixin, session_scope, get_or_create
from qualys.report import  Report
from qualys.scan import Scan, process_scan
from qualys.server import Server, ServerCMDB

logger = logging.getLogger('qualys.request')


def get_all_requests(session):
    db_list = session.query(Request).filter(
        and_(Request.status.in_(status.values()), Request.status.notin_([status['FINISHED'], status['FAILED']]))).all()
    return {db_instance.id for db_instance in db_list}


def get_new_requests(session):
    db_list = session.query(Request).filter(Request.status == status['NEW']).all()
    return {db_instance.id for db_instance in db_list}


def process_request(id):
    with session_scope() as session:
        session.query(Request).get(id).start(session)

def update_request_status(id, status, session):
    session.query(Request.status).filter_by(id=id).update({'status': status})


class Request(BaseMixin, Base):
    """
    QualysScan is responsible for scan related requests to qualys api and data in qualys_scan table.
    """
    id = Column(Integer, primary_key=True)
    title = Column(String(30), nullable=False)
    status = Column(String(50), nullable=False, default=status['NEW'])
    ip = Column(String(300), nullable=False)
    owner = Column(String(30), nullable=False)

    servers = association_proxy('request_servers', 'server', creator=lambda id, server: Request2Server(server=server))

    # @orm.reconstructor
    # def __init__(self, *args, **kwargs):
    #     """
    #         TODO: check if instance is correct type
    #     """
    #     super().__init__(*args, **kwargs)
    #     self.error_log = []

    def start(self, session):
        logger.info('starting request {}'.format(self.id))
        try:
            if self.status == status['NEW'] or not self.servers:
                self.status = status['RUNNING']
                session.commit()
                self._initialize_servers(session)
            self._launch_scans(session)
            if all([scan.status == status['FAILED'] for scan in self.scans]):
                self.status = status['FAILED']
                return
            self._launch_report(session)

        except Exception:
            logger.exception('request {} failed'.format(self.id))
            logger.info('performing session rollback')
            session.rollback()
            self.status = status['FAILED']
            logger.info('commiting failed status')
            session.commit()
        else:
            self.status = status['FINISHED']


    def _initialize_servers(self, session):
        """
        Initializes self.servers with QualysServer2Req instances based on self._ip list

        Returns:
            Dictionary of initialized servers

        Notes:
            In case of server initialization failure server is ignored and error is logged
        """
        logger.info('running _initialize servers')
        current_servers = list(self.servers.keys())
        for ip in self.ip.split(','):
            if ip not in current_servers:
                self.servers[ip] = get_or_create(session, Server, ip=ip)
                current_servers.append(ip)

    def _launch_scans(self, session):
        """
        Launches scans - one thread per region - and  waits till finished

        Returns:
            None


        """
        if not self.scans:
            self._initialize_new_scans(session)

        scan_id_list = [scan.id for scan in self.scans if scan.status not in [status['FINISHED'], status['FAILED']]]

        if not scan_id_list:
            return

        # with thr_pool(max_workers=6, thread_name_prefix='-'.join(['req', str(self.id), 'scan'])) as executor:
        #     future_to_id = {executor.submit(process_scan, id): id for id in scan_id_list}
        #     for future in concurrent.futures.as_completed(future_to_id):
        #         try:
        #             future.result()
        #         except:
        #             logger.error('scan id {} failed'.format(future_to_id[future]))

        with thr_pool(max_workers=6, thread_name_prefix='-'.join(['req', str(self.id), 'scan'])) as executor:
            # future_to_id = {}
            # future_to_id[executor.submit(process_scan, id)] = id
            future_to_id = {executor.submit(process_scan, id): id for id in scan_id_list}
            # for future, id in [future_id for future_id in future_to_id.items() if future_id[0].done()]:
            done = [future_id for future_id in future_to_id.items() if future_id[0].done()]
            logger.info('threads done: {}'.format(done))
            for future, id in done:
                try:
                    future.result()
                except BaseException:
                    # maybe set request to failed
                    print('sna raised exception !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                    logger.exception('scan {} process raised exception'.format(id))
                else:
                    logger.info('scan {} thread finished correctly'.format(id))
                finally:
                    future_to_id.pop(future)
        session.commit()


    def _initialize_new_scans(self, session):
        prefix = 'oat-req{}-scan'.format(self.id)
        time_stamp = datetime.datetime.utcnow().strftime('%y%m%d%H%M')


        platform_region = session.query(ServerCMDB.platform, ServerCMDB.region).distinct().all()
        scan_list = []
        for platform, region, in platform_region:
            title = '-'.join([prefix, platform, region, self.owner, time_stamp])
            scan = Scan(title=title, status=status['NEW'], platform=platform, region=region)
            scan_list.append(scan)

        self.scans.extend(scan_list)
        session.commit()

    def _launch_report(self, session):
        if not self.report:
            prefix = 'oat-req{}-report'.format(self.id)
            time_stamp = datetime.datetime.utcnow().strftime('%y%m%d%H%M')
            title = '-'.join([prefix,self.owner, time_stamp])
            self.report = Report(title=title, status=status['NEW'])
            session.commit()

        if self.report.status not in [status['FINISHED'], status['FAILED']]:
            self.report.start(session)
