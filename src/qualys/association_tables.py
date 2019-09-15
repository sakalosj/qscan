from sqlalchemy import Integer, Column, String, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection

from qualys import BaseMixin, Base


class Request2Server(BaseMixin, Base):
    request_id_fk = Column(Integer, ForeignKey('request.id'), primary_key=True)
    server_id_fk = Column(Integer, ForeignKey('server.id'), primary_key=True)
    server_ip = association_proxy('server', 'ip')
    status = Column(String(30))
    data = Column(String(30))
    error = Column(String(30))

    request = relationship('Request', backref=backref('request_servers', collection_class=attribute_mapped_collection('server_ip')))
    server = relationship('Server', backref=backref('server_requests'))

    patches = association_proxy('request_server2patch', 'patch', creator=lambda patch: Server2Patch(patch=patch))
    vulners = association_proxy('request_server2vulner', 'vulner', creator=lambda vulner: Server2Vulner(vulner=vulner))


class Server2Patch(BaseMixin, Base):
    request2server_request_id_fk = Column(Integer, ForeignKey('request2server.request_id_fk'), primary_key=True)
    request2server_server_id_fk = Column(Integer, ForeignKey('request2server.server_id_fk'), primary_key=True)
    patch_qid_fk = Column(Integer, ForeignKey('patch.qid'), primary_key=True)

    request_server = relationship('Request2Server', backref=backref('request_server2patch'), foreign_keys=[request2server_request_id_fk, request2server_server_id_fk])
    patch = relationship('Patch', backref=backref('request_servers2patch'), foreign_keys=[patch_qid_fk])

    __table_args__ = (ForeignKeyConstraint([request2server_request_id_fk, request2server_server_id_fk],
                                           [Request2Server.request_id_fk, Request2Server.server_id_fk]),
                      {})


class Server2Vulner(BaseMixin, Base):
    request2server_request_id_fk = Column(Integer, ForeignKey('request2server.request_id_fk'), primary_key=True)
    request2server_server_id_fk = Column(Integer, ForeignKey('request2server.server_id_fk'), primary_key=True)
    vulner_qid_fk = Column(Integer,ForeignKey('vulner.qid'), primary_key=True)

    request_servers = relationship('Request2Server', backref=backref('request_server2vulner'), foreign_keys=[request2server_request_id_fk, request2server_server_id_fk])
    vulner = relationship('Vulner', backref=backref('request_server2vulner'), foreign_keys=[vulner_qid_fk])

    __table_args__ = (ForeignKeyConstraint([request2server_request_id_fk, request2server_server_id_fk],
                                           [Request2Server.request_id_fk, Request2Server.server_id_fk]),
                      {})


