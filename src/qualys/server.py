import re

from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound

from qualys import cfg, BaseMixin, ScopedSession, Base
import logging
import ipaddress



logger = logging.getLogger('qualys.server')
#
# def get_or_create(session, model, **kwargs):
#     instance = session.query(model).filter_by(**kwargs).first()
#     if instance:
#         return instance
#     else:
#         instance = model(**kwargs)
#         session.add(instance)
#         session.commit()
#         return instance


class Server(BaseMixin, Base):
    """
    Class responsible for servers in reports and maintains qualys_server table
    """

    id = Column(Integer, primary_key=True)
    ip = Column(String(30), nullable=False)
    hostname = Column(String(30))
    server_cmdb_id_fk = Column(Integer, ForeignKey('cmdb.server.id'), nullable=False)
    server_cmdb = relationship('ServerCMDB', backref=backref('server_qualys', uselist=False))
    last_report = Column(String(30))
    status = Column(String(15))
    region = association_proxy('server_cmdb', 'region')
    platform = association_proxy('server_cmdb', 'platform')

    __table_args__ = (UniqueConstraint(ip, hostname, server_cmdb_id_fk),
                      {})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        session = ScopedSession()
        self.validate_server_cmdb_id_fk(session)
        session.commit()

    def validate_server_cmdb_id_fk(self, session, rewrite=True):
        try:
            server_cmdb_id_fk = session.query(ServerCMDB.id).filter(ServerCMDB.ip == self.ip).one()[0]
        except NoResultFound:
            logger.error('server not found in cmdb')
            raise
        if self.server_cmdb_id_fk != server_cmdb_id_fk and rewrite:
            self.server_cmdb_id_fk = server_cmdb_id_fk
        elif self.server_cmdb_id_fk != server_cmdb_id_fk and not rewrite:
            raise AttributeError('incorect server_cmdb_id_fk')



class ServerCMDB(BaseMixin, Base):
    __tablename__ = 'server'
    __table_args__ = (
        {'schema': 'cmdb'}
    )

    id = Column(Integer, primary_key=True)
    hostname = Column(String(30),nullable=False)
    ip = Column(String(30),nullable=False, unique=True)
    platform = Column(String(30),nullable=False)
    region = Column(String(30),nullable=False)
