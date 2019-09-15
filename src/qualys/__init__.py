from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker


engine_qualys = create_engine('mysql+pymysql://qualys:123456@localhost/qualys_scan_test')
Base = declarative_base()
ScopedSession = scoped_session(sessionmaker(bind=engine_qualys))




@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = ScopedSession()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class BaseMixin:
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


class AssocBaseMixin:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __repr__(self):
        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in self.__table__.c.keys())
        return "%s(%s)" % (self.__class__.__name__, values)

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


from .request import Request
from .server import Server
from .server import ServerCMDB
from .scan import Scan
from .report import Report
from .vulner import Vulner
from .patch import Patch
