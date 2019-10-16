import json

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError

from qualys import Base, engine_qualys, ServerCMDB

if __name__ == '__main__':
    engine = create_engine('mysql+pymysql://root:123456@localhost:3307/')
    conn = engine.connect()
    conn.execute("commit")
    try:
        conn.execute("create database qualys_scan")
    except ProgrammingError as e:
        print(e)

    try:
        conn.execute("create database cmdb")
    except ProgrammingError as e:
        print(e)

    conn.close()

    Base.metadata.create_all(engine_qualys)

    session = sessionmaker(bind=engine)()
    with open('datafiles/cmdb_server_data.json','r') as f:
        data = json.loads(f.read())
    for server in data:
        s = ServerCMDB(**server)
        session.add(s)
    session.commit()





