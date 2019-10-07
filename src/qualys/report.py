import logging
import time

import session_pool
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, orm
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref

from hlp.const import status, methods, stat
from qualys import BaseMixin, Base
import qualys.api as api
# from qualys.api import Api
from qualys.patch import Patch
from qualys.vulner import Vulner

logger = logging.getLogger(__name__)

# config = configparser.ConfigParser()
# config.read('src/qualys_scan.conf')
# api_url = config['qg_rest_api']['api_url']
api_url = 'http://localhost:5000/api/v1.0/'
section = 'report'
base_url = '/'.join([api_url, section])


class Report(BaseMixin, Base):
    """
    Class is responsible for report objects lifecycle and data in qualys_report table.
    """
    id = Column(Integer, primary_key=True)
    qid = Column(Integer)
    request_id_fk = Column(Integer, ForeignKey('request.id'), nullable=False)

    title = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False)
    launched = Column(DateTime)
    request = relationship("Request", backref=backref("report", uselist=False))

    servers = association_proxy('request', 'servers')

    def init_api(self):
        self.api = api.Api(section='reports')

    def start(self, session):
        self.init_api()
        try:
            if self.status == stat.NEW:
                self._launch_report()
                session.commit()
            json_data = self._get_result()
            self._process_response(json_data, session)

        except Exception as e:
            logger.exception('report {} raised:'.format(self.id))
            session.rollback()
            self.status = stat.FAILED
            session.commit()
            return

        if json_data['status'] == stat.FAILED:
            session.commit()
            return
        self.status = stat.FINISHED
        session.commit()

    def _launch_report(self) -> None:
        """
        Returns:

        TODO: add validation of returned json
        """

        report_dict = {"servers": self._get_ip_list(), "title": self.title}

        json_data = self.api.post(report_dict)
        self.qid = json_data['id']
        self.status = status['RUNNING']

    def _get_ip_list(self) -> list:
        """ Generates ip list based on associated server self.servers
        association via association proxy Report.servers->Request.servers->Request2Server->Server

        Returns:
            ip list
        """
        return list(self.servers.keys())

    def _get_result(self, sleep_time=3, timeout=600) -> dict:
        """

        Args:
            sleep_time: wait time between calls
            timeout: max running time (+wait time in worst case)

        Returns:
            dictionary returned by api

        """
        start_time = time.time()
        while True:
            json_data = self.api.get(self.qid)
            # even if returned status is unknown, it should end in valid state
            if json_data['status'] in [stat.FINISHED, stat.FAILED]:
                break
            if (time.time() - start_time) > timeout:
                raise TimeoutError('report {} dindt received finished/failed status'.format(self.id))
            time.sleep(sleep_time)
        return json_data

    def _process_response(self, response_data, session) -> None:
        """
        Method to process returned data.

        Args:
            response_data: json data
            session: sqlalchemy session

        Returns:
            None

        TODO:
            check if response server is associated wit report

        """
        logger.info('processing report {} data: {}'.format(self.id, response_data))
        self.qid = response_data['id']
        for ip, patch_vulner in response_data['servers_data'].items():
            logger.info('processing ip: {}'.format(ip))
            self.servers[ip].last_report = self.id

            # for patch in patch_vulner['patches']:
            #     logger.info('Processing patch: {}'.format(patch))
            #     if patch['qid'] not in [patch.qid for patch in self.request.request_servers[ip].patches]:
            #         patch = Patch.get_one_or_create(session, **patch)
            #         self.request.request_servers[ip].patches.append(patch)
            self._process_response_patches(session, ip, patch_vulner['patches'])

            # for vulner in patch_vulner['vulners']:
            #     if vulner['qid'] not in [vulner.qid for vulner in self.request.request_servers[ip].vulners]:
            #         vulner = Vulner.get_one_or_create(session, **vulner)
            #         self.request.request_servers[ip].vulners.append(vulner)
            self._process_response_vulners(session,ip, patch_vulner['vulners'])

    def _process_response_patches(self, session, ip, patches: list) -> None:
        """
        Processing patches from resonse for specific ip
        Args:
            session: sqlalchemy session
            ip: server ip
            patches: list of patches to process

        Returns:
            None

        """
        for patch in patches:
            logger.info('Processing patch: {}'.format(patch))
            if patch['qid'] not in [patch.qid for patch in self.request.request_servers[ip].patches]:
                patch = Patch.get_one_or_create(session, **patch)
                self.request.request_servers[ip].patches.append(patch)

    def _process_response_vulners(self, session, ip, vulners: list) -> None:
        """
        Processing vulners from resonse for specific ip
        Args:
            session: sqlalchemy session
            ip: server ip
            vulneres: list of vulneres to process

        Returns:
            None

        """
        for vulner in vulners:
            logger.info('Processing vulner: {}'.format(vulner))
            if vulner['qid'] not in [vulner.qid for vulner in self.request.request_servers[ip].vulners]:
                vulner = Vulner.get_one_or_create(session, **vulner)
                self.request.request_servers[ip].vulners.append(vulner)


    def row_counts(self):
        print('server count', len(self.servers.keys()))
        for ip in self.servers.keys():
            print('\tserver', ip)
            print('\t\t patches', len(self.request.request_servers[ip].patches))
            print('\t\t vulners', len(self.request.request_servers[ip].vulners))
        print()
