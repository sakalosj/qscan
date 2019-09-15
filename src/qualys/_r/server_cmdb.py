from sqlalchemy import Column, Integer, String

from qualys import BaseMixin, Base


class ServerCMDB(Base):
    __tablename__ = 'server'
    __table_args__ = (
        {'schema': 'data_test'}
    )

    id = Column(Integer, primary_key=True)
    hostname = Column(String(30))
    cmdb_ip_address = Column(String(30))
    cmdb_category = Column(String(30))
    cmdb_folder = Column(String(30))
