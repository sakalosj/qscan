from contextlib import contextmanager

from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base, declared_attr, DeclarativeMeta
from sqlalchemy.orm import scoped_session, sessionmaker

from .const import status

# e = create_engine("sqlite:///datafiles/data.sqlite", connect_args={'check_same_thread': False})
engine_qualys = create_engine('mysql+pymysql://qualys:123456@localhost/qualys_scan_test')
Base = declarative_base()
Base.metadata.create_all(engine_qualys)

# engine_data = create_engine('mysql+pymysql://qualys:123456@localhost/data')
# Base = declarative_base()
# Base.metadata.create_all(engine_data)
ScopedSession = scoped_session(sessionmaker(bind=engine_qualys))

from .tables import Request, Server, ServerCMDB, Scan, Report, Patch, Vulner


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


class AssocBaseMixin():

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __repr__(self):
        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in self.__table__.c.keys())
        return "%s(%s)" % (self.__class__.__name__, values)


class Proxy:
    """
    TODO:
    self db_instance - readonly
    make db_fields private

    """
    ScopedSession = ScopedSession
    def __init__(self, pk, *args, **kwargs):
        if not getattr(self, '__db_model__', False) :
            raise AttributeError('<class>.__db_model__ nod defined')
        if not issubclass(type(self.__db_model__), DeclarativeMeta):
            raise AttributeError('{} is not slqlalchemy Base'.format(self.__db_model__))
        # if not isinstance(pk, self.__db_model__):
        #     raise AttributeError('incorrect db instance')

        self._db_instance = ScopedSession.query(self.__db_model__).get(pk)
        # self.____db_model__ = __db_model__
        self._db_fields = [item for item in inspect(self.__db_model__).mapper.all_orm_descriptors.__dir__() if '__' not in item]
        self._db_fields.append('_sa_instance_state')
        super().__init__(*args, **kwargs)

    def __getattr__(self, item):
        if item != '_db_fields' and item in self._db_fields:
            return getattr(self._db_instance, item)
        else:
            print(item)
            raise AttributeError

    def __setattr__(self, key, value):
        if key in getattr(self, '_db_fields', []):
            object.__setattr__(self._db_instance, key, value)
        else:
            object.__setattr__(self, key, value)


    def update(self):
        session = ScopedSession()
        if inspect(self._db_instance).session_id == session.hash_key:
            session.commit()
        else:
            self._db_instance = session.merge(self._db_instance)
            session.commit()


class PKNotFoundError(BaseException):
    """Exception raised when Proxy response contains error code

    Attributes:
        code -- error number contained in response
        text -- text contained in response
    """

    def __init__(self, code, text):
        self.code = code
        self.text = text
