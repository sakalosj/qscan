"""
Module responsible for handlig requests.
mapped to db table 'request' via sqlalchemy orm.
"""
import datetime
import logging
import time
from concurrent.futures.thread import ThreadPoolExecutor as thr_pool

from sqlalchemy import and_, Column, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy

from hlp.const import status
from qualys.association_tables import Request2Server
from . import Base, BaseMixin, session_scope, get_or_create, get_new_engine_session
from qualys.report import Report
from qualys.scan import Scan, process_scan, process_scan_q
from qualys.server import Server, ServerCMDB

logger = logging.getLogger('qualys.request')


def get_all_requests(session) -> set:
    """
    function to gather all not finished or failed requests.

    Args:
        session: sqlalchemy session

    Returns:
        None

    """
    db_list = session.query(Request).filter(
        and_(Request.status.in_(status.values()), Request.status.notin_([status['FINISHED'], status['FAILED']]))).all()
    return {db_instance.id for db_instance in db_list}


def get_new_requests(session) -> set:
    """
    function to gather new requests

    Args:
        session: sqlalchemy session

    Returns:
        None

    """
    db_list = session.query(Request).filter(Request.status == status['NEW']).all()
    return {db_instance.id for db_instance in db_list}


def process_request(id: int) -> None:
    """
    wrapper function to start request processing. Main purpose is to be able to start also constructor in new thread,
    because of sqlalchemy session concurrency support.

    Args:
        id: id of entry in request table

    Returns:

    """
    with session_scope() as session:
        session.query(Request).get(id).start(session)

def process_request_q(id: int, redis_queue) -> None:
    """
    wrapper function to start request processing via redis queue. Because of worker is running in new process sqlclhemy requires new  engine

    Args:
        id: id of entry in request table

    Returns:

    """
    print('get session')
    session = get_new_engine_session()
    print('starting request')
    session.query(Request).get(id).start(session, redis_queue)


def update_request_status(id: int, status: str, session) -> None:
    """
    function to update request status without creating sqlalchemy instance. Main usage in case request processing failed
    with exception and was unable to update status.

    Args:
        id: id of  entry in request table
        status: new status
        session: sqlalchemy session

    Returns:
        None

    """
    session.query(Request.status).filter_by(id=id).update({'status': status})


class Request(BaseMixin, Base):
    """
    Request responsible for request flow and required data initialization.
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

    def start(self, session, redis_queue) -> None:
        """
        main function, representing object licfecycle calling other

        Args:
            session: sqlalchemy session

        Returns:

        """
        logger.info('starting request {}'.format(self.id))
        try:
            if self.status == status['NEW'] or not self.servers:
                self.status = status['RUNNING']
                session.commit()
                self._initialize_servers(session)
            self._launch_scans(session, redis_queue)
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
        else:
            self.status = status['FINISHED']
        finally:
            session.commit()

    def _initialize_servers(self, session) -> None:
        """
        initializes servers

        Returns:
            None
        """
        logger.info('running _initialize servers')
        current_servers = list(self.servers.keys())
        for ip in self.ip.split(','):
            if ip not in current_servers:
                self.servers[ip] = get_or_create(session, Server, ip=ip)
                # # potential deadlock ???
                # self.servers[ip].validate_server_cmdb_id_fk(session)
                current_servers.append(ip)

    def _launch_scans(self, session, redis_queue) -> None:
        """
        Launches scans - one thread per region and location

        Returns:
            None


        """

        if not self.scans:
            self._initialize_new_scans(session)

        scan_id_list = [scan.id for scan in self.scans if scan.status not in [status['FINISHED'], status['FAILED']]]

        if not scan_id_list:
            return

        scan_jobs ={id: redis_queue.enqueue(process_scan_q, id) for id in scan_id_list}


        while scan_jobs:
            for id, scan_job in list(scan_jobs.items()):
                if scan_job.is_finished:
                    logger.info('scan {} thread finished correctly'.format(id))
                    scan_jobs.pop(id)
                if scan_job.is_failed:
                    # maybe set request to failed
                    logger.exception('scan {} failed'.format(id))
            time.sleep(1)

        # with thr_pool(max_workers=6, thread_name_prefix='-'.join(['req', str(self.id), 'scan'])) as executor:
        #     future_to_id = {executor.submit(process_scan, id): id for id in scan_id_list}
        #     done = [future_id for future_id in future_to_id.items() if future_id[0].done()]
        #     logger.info('threads done: {}'.format(done))
        #     for future, id in done:
        #         try:
        #             future.result()
        #         except BaseException:
        #             # maybe set request to failed
        #             print('sna raised exception !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        #             logger.exception('scan {} process raised exception'.format(id))
        #         else:
        #             logger.info('scan {} thread finished correctly'.format(id))
        #         finally:
        #             future_to_id.pop(future)
        session.commit()

    def _initialize_new_scans(self, session) -> None:
        """
        Initializes scans based on their platform and location

        Args:
            session:

        Returns:

        """
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

    def _launch_report(self, session) -> None:
        """
        Launching report
        Args:
            session:

        Returns:

        """
        if not self.report:
            prefix = 'oat-req{}-report'.format(self.id)
            time_stamp = datetime.datetime.utcnow().strftime('%y%m%d%H%M')
            title = '-'.join([prefix, self.owner, time_stamp])
            self.report = Report(title=title, status=status['NEW'])
            session.commit()

        if self.report.status not in [status['FINISHED'], status['FAILED']]:
            self.report.start(session)
