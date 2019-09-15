import csv
import json
import logging
import queue
import time

import configparser

from session_pool.session_pool import send_task
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref

from hlp.const import status
from qualys import BaseMixin, Base
from qualys.patch import Patch
from qualys.vulner import Vulner

logger = logging.getLogger('qualys.report')

config = configparser.ConfigParser()
config.read('qualys_scan.conf')

class Report(BaseMixin, Base):
    """
    Class is responsible for report objects lifecycle and data in qualys_report table.
    """
    id = Column(Integer, primary_key=True)
    qid = Column(Integer)
    request_id_fk = Column(Integer, ForeignKey('request.id'),nullable=False)

    title = Column(String(50),nullable=False)
    status = Column(String(30),nullable=False)
    launched = Column(DateTime)
    request = relationship("Request", backref=backref("report",uselist=False))

    servers = association_proxy('request', 'servers')

    def start(self, session):
        try:
            if self.status == status['NEW']:
                self._launch_report()
            json_data = self._get_result()
            self._process_response(json_data, session)
        except Exception as e:
            # logger.exception('report {} raised:'.format(self.id))
            logger.error('report {} raised:'.format(self.id))
            session.rollback()
            self.status = status['FAILED']
            session.commit()
            # raise

        if json_data['status'] == status['FAILED']:
            session.commit()
            return
        self.status = status['FINISHED']
        session.commit()

    def _launch_report(self):
        method = 'post'
        url = 'http://localhost:5000/api/v1.0/reports'
        report_dict = {"servers": list(self.servers.keys()), "title": self.title}
        options = {'json': report_dict}

        response = send_task(method, url, options)
        json_data = response.json()

        self.qid = json_data['id']
        self.status = status['RUNNING']

    def _get_result(self, ):
        method = 'get'
        url = 'http://localhost:5000/api/v1.0/reports/{}'.format(self.qid)

        while True:
            json_data = send_task(method, url, return_json=True)
            if json_data['status'] in [status['FINISHED'], status['FAILED']]:
                break
            time.sleep(3)
        return json_data

    def _process_response(self, response_data, session):
        logger.info('processin report {} data: {}'.format(self.id, response_data))
        self.qid = response_data['id']
        for ip, patch_vulner in response_data['servers_data'].items():
            logger.info('processing ip: {}'.format(ip))
            self.servers[ip].last_report = self.id

            for patch in patch_vulner['patches']:
                logger.info('Processing patch: {}'.format(patch))
                if patch['qid'] not in [patch.qid for patch in self.request.request_servers[ip].patches]:
                    patch_from_db =  session.query(Patch).filter_by(**patch).with_for_update().one_or_none()
                    if patch_from_db :
                        patch = patch_from_db
                    else:
                        patch = Patch(**patch)
                    # patch = session.query(Patch).filter_by(**patch).with_for_update().one_or_none() or Patch(**patch)
                    self.request.request_servers[ip].patches.append(patch)

            for vulner in patch_vulner['vulners']:
                if vulner['qid'] not in [vulner.qid for vulner in self.request.request_servers[ip].vulners]:
                    self.request.request_servers[ip].vulners.append(
                        session.query(Vulner).filter_by(**vulner).with_for_update().one_or_none() or
                        Vulner(**vulner)
                    )

    def row_counts(self):
        print('server count', len(self.servers.keys()))
        for ip in self.servers.keys():
            print('\tserver',ip)
            print('\t\t patches', len(self.request.request_servers[ip].patches))
            print('\t\t vulners', len(self.request.request_servers[ip].vulners))
        print()

