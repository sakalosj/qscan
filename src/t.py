import os
from threading import get_ident
from time import sleep

from sqlalchemy import create_engine

from qualys.controller import redis_queue
from qualys.db import ScopedSession, get_new_engine_session, init_db
from qualys import api
from qualys.request import Request, t
from qualys.scan import Scan


s = ScopedSession()

e = create_engine('mysql+pymysql://root:123456@localhost:3307/qualys_scan')
ses1 = get_new_engine_session()


def test_db():
    s = get_new_engine_session()
    print(s.query(Scan).first())
    print(os.getpid())
    print(get_ident())
    for _ in range(5):
        sleep(2)


def test_request(i):
    # req = Request(title='req test',ip='10.0.1.3,20.0.1.3,20.0.2.1,30.0.1.3,10.0.2.3', owner='null_user')
    for i in range(i):
        req = Request(title='req{} test'.format(i),
                      ip='10.0.1.1,10.0.1.2,10.0.1.3,20.0.1.1,20.0.1.2,20.0.1.3,30.0.1.1,30.0.1.2,30.0.1.3,10.0.2.1,10.0.2.2,10.0.2.3,20.0.2.1,20.0.2.2,20.0.2.3,30.0.2.1,30.0.2.2,30.0.2.3',
                      owner='null_user')
        s.add(req)
    s.commit()
    # process_request(req.id)
    return req.id


def add_req(i):
    # req = Request(title='req test',ip='10.0.1.3,20.0.1.3,20.0.2.1,30.0.1.3,10.0.2.3', owner='null_user')
    for i in range(i):
        req = Request(title='req{} test'.format(i),
                      ip='10.0.1.1,10.0.1.2,10.0.1.3,20.0.1.1,20.0.1.2,20.0.1.3,30.0.1.1,30.0.1.2,30.0.1.3,10.0.2.1,10.0.2.2,10.0.2.3,20.0.2.1,20.0.2.2,20.0.2.3,30.0.2.1,30.0.2.2,30.0.2.3',
                      owner='null_user')
        s.add(req)
    s.commit()
    return req


ra = api.Api(section='report')
sa = api.Api(section='scan')

