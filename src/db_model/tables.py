from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Time, ForeignKeyConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import  declared_attr
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection

from db_model import ScopedSession, Base, engine_qualys


class BaseMixin():

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def populate(cls, data_list, session):
        for entry in data_list:
            session.merge(cls(**entry))
        session.commit()

    def __repr__(self):
        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in self.__table__.c.keys())
        return "%s(%s)" % (self.__class__.__name__, values)

class AssocBaseMixin():

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __repr__(self):
        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in self.__table__.c.keys())
        return "%s(%s)" % (self.__class__.__name__, values)

# def cr(server,)
class Request(BaseMixin, Base):
    id = Column(Integer, primary_key=True)
    title = Column(String(30))
    status = Column(String(30))
    ip = Column(String(300))
    option_title = Column(String(30))
    priority = Column(Integer)
    owner = Column(String(30))

    # servers = association_proxy('request_servers', 'server', creator=lambda server: Request2Server(server=server))
    # servers = association_proxy('request_servers', 'server', creator=lambda ip, server:Request2Server(server=server, server_ip_fk=ip))
    servers = association_proxy('request_servers', 'server', creator=lambda ip, server: Request2Server(server=server, server_ip_fk=ip))


class Server(BaseMixin, Base):
    ip = Column(String(30), primary_key=True, autoincrement=False)
    server_cmdb_id_fk = Column(Integer, ForeignKey('cmdb.server.id'))
    server_cmdb = relationship('ServerCMDB', backref=backref('server_qulays', uselist=False))
    last_report = Column(String(30))
    status = Column(String(15))
    region = association_proxy('server_cmdb', 'region')


class Request2Server(BaseMixin, Base):
    request_id_fk = Column(Integer, ForeignKey('request.id'), primary_key=True)
    server_ip_fk = Column(String(30), ForeignKey('server.ip'), primary_key=True)
    status = Column(String(30))
    data = Column(String(30))
    error = Column(String(30))

    # request = relationship('Request', backref=backref('request_servers'))
    request = relationship('Request', backref=backref('request_servers', collection_class=attribute_mapped_collection('server_ip_fk')))
    server = relationship('Server', backref=backref('server_requests'))

    patches = association_proxy('request_server2patch', 'patch', creator=lambda patch: Server2Patch(patch=patch))
    vulners = association_proxy('request_server2vulner', 'vulner', creator=lambda vulner: Server2Vulner(vulner=vulner))


class ServerCMDB(BaseMixin, Base):
    __tablename__ = 'server'
    __table_args__ = (
            {'schema': 'cmdb'}
            )

    id = Column(Integer, primary_key=True)
    hostname = Column(String(30))
    ip = Column(String(30))
    category = Column(String(30))
    region = Column(String(30))


class Scan(BaseMixin, Base):
    id = Column(Integer, primary_key=True)
    request_id_fk = Column(Integer, ForeignKey('request.id'))
    region = Column(String(30), nullable=False)
    scan_title = Column(String(30))
    status = Column(String(30))
    ip = Column(String(30))
    option_title = Column(String(30))
    iscanner_name = Column(String(30), nullable=False)
    priority = Column(String(30))
    datetime = Column(DateTime)


class Report(BaseMixin,Base):
    id = Column(Integer, primary_key=True)
    request_id_fk = Column(Integer, ForeignKey('request.id'))
    title = Column(String(30))
    duration = Column(Time)
    status = Column(String(30))
    launched = Column(DateTime)
    size = Column(String(30))
    message = Column(String(30))


class Patch(BaseMixin, Base):
    qid = Column(Integer, primary_key=True)
    vulners = relationship('Vulner', backref='patch')
    severity = Column(Integer)
    title = Column(String(30))
    # category = Column(String(30))
    # solution = Column(String(30))
    dhl_category = Column(String(30))
    dhl_type = Column(String(30))


class Server2Patch(BaseMixin, Base):
    request2server_request_id_fk = Column(Integer, ForeignKey('request2server.request_id_fk'), primary_key=True)
    request2server_server_ip_fk = Column(String(30), ForeignKey('request2server.server_ip_fk'), primary_key=True)
    patch_qid_fk = Column(Integer, ForeignKey('patch.qid'), primary_key=True)

    request_server = relationship('Request2Server', backref=backref('request_server2patch'), foreign_keys=[request2server_request_id_fk, request2server_server_ip_fk])
    patch = relationship('Patch', backref=backref('request_servers2patch'), foreign_keys=[patch_qid_fk])

    __table_args__ = (ForeignKeyConstraint([request2server_request_id_fk, request2server_server_ip_fk],
                                           [Request2Server.request_id_fk, Request2Server.server_ip_fk]),
                      {})


class Vulner(BaseMixin, Base):
    qid = Column(Integer, primary_key=True)
    patch_qid_fk = Column(Integer, ForeignKey('patch.qid'))
    severity = Column(Integer)
    cveid = Column(Integer)
    title = Column(String(30))
    category = Column(String(30))
    solution = Column(String(30))
    dhl_category = Column(String(30))
    dhl_type = Column(String(30))


class Server2Vulner(BaseMixin, Base):
    request2server_request_id_fk = Column(Integer, ForeignKey('request2server.request_id_fk'), primary_key=True)
    request2server_server_ip_fk = Column(String(30), ForeignKey('request2server.server_ip_fk'), primary_key=True)
    vulner_qid_fk = Column(Integer,ForeignKey('vulner.qid'), primary_key=True)

    request_servers = relationship('Request2Server', backref=backref('request_server2vulner'), foreign_keys=[request2server_request_id_fk, request2server_server_ip_fk])
    vulner = relationship('Vulner', backref=backref('request_server2vulner'), foreign_keys=[vulner_qid_fk])

    __table_args__ = (ForeignKeyConstraint([request2server_request_id_fk, request2server_server_ip_fk],
                                           [Request2Server.request_id_fk, Request2Server.server_ip_fk]),
                      {})


# s = Session()
# def cleandb():
#     for tbl in reversed(Base.metadata.sorted_tables):
#         engine_qualys.execute(tbl.delete())
#
# # Base.metadata.create_all(engine_qualys)
#
# request1 = Request(scan_title='tttt',ip='10.0.1.1')
# scan1 = Scan(region='EMEA',status='Finished', iscanner_name = 'Null', request_id_fk=435,id='1000')
# report1 = Report(request_id_fk=435,id=1)
# server1 = Server(ip='30.0.1.3',server_id_fk=9)
#
# server=s.query(Server).first()
# request=s.query(Request).first()
# r2s=s.query(Request2Server).filter(and_(Request2Server.request==request, Request2Server.server==server)).first()
#
# patch1=s.query(Patch).first()
# request2=s.query(Request).all()[1]
# r2s = s.query(Request2Server).filter(and_(Request2Server.request==request2, Request2Server.server==server)).first()
# # s.add_all([request1, scan1, report1, server1])
# # s.commit()
