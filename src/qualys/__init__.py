from contextlib import contextmanager

from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker


engine_qualys = create_engine('mysql+pymysql://root:123456@localhost:3307/qualys_scan')
Base = declarative_base()
ScopedSession = scoped_session(sessionmaker(bind=engine_qualys))

def get_new_engine_session():
    e = create_engine('mysql+pymysql://root:123456@localhost:3307/qualys_scan')
    return sessionmaker(bind=e)()


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
    def get_one_or_create(cls, session, **kwargs):
        instance = session.query(cls).filter_by(**kwargs).with_for_update().one_or_none()

        if not instance:
            pk = [key.name for key in inspect(cls).primary_key]
            q = session.query(cls).filter_by(**{key: value for key, value in kwargs.items() if key in pk})
            # check if kwargs contains pk and if yes check if pk exists in db
            if set(pk).issubset(kwargs.keys()) and session.query(q.exists()).scalar():
                # error because first query failed, no entry with all matching fileds exists, but pk exist
                raise ValueError('attributes contain existing pk, but other values dont match db')
            instance = cls(**kwargs)

        return instance

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
