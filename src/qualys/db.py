import json
from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker

from hlp.cfg import QS_DB_URI

servercmdb_data_file = 'datafiles/cmdb_server_data.json'

engine = create_engine(QS_DB_URI)
Base = declarative_base()
ScopedSession = scoped_session(sessionmaker(bind=engine))

def check_if_db_exist(db_uri, db=None):
    """
    Checks if db exist. If db is provided it is checked instead of parsed from uri
    Args:
        db_uri: DSN string
        db: db name

    Returns:
        bool

    TODO: improve overall parsing (no technical format definition found)

    """
    db_uri, db_from_uri = db_uri.rsplit('/', 1)

    if not db:
        db = db_from_uri

    engine = create_engine(db_uri)
    result = engine.execute(
        text('SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :db').bindparams(
            db=db)).fetchall()
    return bool(result)


def init_db(db_uri):
    db_uri, db = db_uri.rsplit('/', 1)
    engine = create_engine(db_uri)
    conn = engine.connect()

    stmt = text('SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :db')

    if not conn.execute(stmt.bindparams(db='qualys_scan')).fetchall() or not engine.execute(
            stmt.bindparams(db='cmdb')).fetchall():
        conn.execute('create database if not exists qualys_scan')
        conn.execute('create database if not exists cmdb')

        engine.execute('use qualys_scan')
        Base.metadata.create_all(engine)
        servercmdb_data = get_data_from_file(servercmdb_data_file)
        init_servercmdb_table(engine, servercmdb_data)

    conn.close()
    return engine


def get_data_from_file(file_name):
    with open(file_name, 'r') as f:
        data = json.loads(f.read())
    return data


def init_servercmdb_table(engine, data):
    from qualys.server import ServerCMDB

    session = sessionmaker(bind=engine)()
    for server in data:
        s = ServerCMDB(**server)
        session.add(s)
    session.commit()

def get_new_engine_session():
    """
    Provides session bound to new engine. Required because of RQ worker natively supports only one process per worker
    and sqlalchemy engines are not designed to be shared among processes

    Returns:
        sqlalchemy session

    """
    e = create_engine(QS_DB_URI)
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
        """
        Sets sqlalchemy table name to lowercase  model class name.

        :return: lowercase name
        """
        return cls.__name__.lower()

    @classmethod
    def get_one_or_create(cls, session, **kwargs):
        """
        Provides entry from table if one was found, creates new if not found.
        Raises Exception if multiple entries were found or if in collection of provided arguments id unique,
        but contains non-unique primary key

        :return:
            sqlalchemy model instance
        """
        if not kwargs:
            raise ValueError('No')
        instance = session.query(cls).filter_by(**kwargs).with_for_update().one_or_none()


        if not instance:
            # pk = [key.name for key in inspect(cls).primary_key]
            # q = session.query(cls).filter_by(**{key: value for key, value in kwargs.items() if key in pk})
            # # check if kwargs contains pk and if yes check if pk exists in db
            # if set(pk).issubset(kwargs.keys()) and session.query(q.exists()).scalar():
            #     # error because first query failed, no entry with all matching fileds exists, but pk exist
            #     raise ValueError('attributes contain existing pk, but other values dont match db')
            instance = cls(**kwargs)
            session.commit()

        return instance

    # @classmethod
    # def populate(cls, data_list, session):
    #
    #     for entry in data_list:
    #         session.merge(cls(**entry))
    #     session.commit()

    def __repr__(self):
        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in self.__table__.c.keys())
        return "%s(%s)" % (self.__class__.__name__, values)


# class AssocBaseMixin:
#
#     @declared_attr
#     def __tablename__(cls):
#         return cls.__name__.lower()
#
#     def __repr__(self):
#         values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in self.__table__.c.keys())
#         return "%s(%s)" % (self.__class__.__name__, values)


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance



