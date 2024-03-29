# -*- coding: utf-8 -*-
"""Example Google style docstrings.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
import json
import queue
import time
import logging

from session_pool.session_pool import send_task
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref

from hlp.const import status
from qualys import Base, BaseMixin, session_scope
from session_pool import SessionPool, TaskRequest

logger = logging.getLogger('qualys.scan')


def process_scan(id):
    with session_scope() as session:
        session.query(Scan).get(id).start(session)


class Scan(BaseMixin, Base):
    """
    QualysScan is responsible for scan related requests to qualys api and data in qualys_scan table.
    """
    id = Column(Integer, primary_key=True)
    qid = Column(Integer)
    request_id_fk = Column(Integer, ForeignKey('request.id'))
    title = Column(String(50))
    status = Column(String(30))
    launched = Column(DateTime)
    region = Column(String(10), nullable=False)
    platform = Column(String(10), nullable=False)

    request = relationship('Request', backref=backref('scans'))
    servers = association_proxy('request', 'servers')

    def start(self, session):
        try:
            if self.status == status['NEW']:
                self._launch_scan()
            result = self._get_result()
        except Exception:
            # logger.exception('scan {} failed'.format(self.id))
            logger.error('scan {} failed'.format(self.id))
            session.rollback()
            self.status = status['FAILED']
            session.commit()
            raise

        if result['status'] == status['FAILED']:
            return
        self.status = status['FINISHED']

    def _launch_scan(self, ):
        url = 'http://localhost:5000/api/v1.0/scans'
        ips = [server.ip for server in self.servers.values() if server.region == self.region and server.platform == self.platform]
        scan_dict = {"servers": ips, "title": self.title}
        options = {'json': scan_dict}

        response = send_task('post', url, options)
        json_data = response.json()
        self.qid = json_data['id']
        self.status = json_data['status']

    def _get_result(self ):

        method = 'get'
        url = 'http://localhost:5000/api/v1.0/scans/{}'.format(self.qid)

        while True:
            json_data = send_task(method, url, return_json=True)
            if json_data['status'] in [status['FINISHED'], status['FAILED']]:
                break
            time.sleep(3)
        return json_data
