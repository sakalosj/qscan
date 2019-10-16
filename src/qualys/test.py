
from session_pool import SessionPool, TaskRequest
from qualys import *









from concurrent.futures import ThreadPoolExecutor as TEX
from time import sleep

s = ScopedSession()
l = [(i, 'n' + str(i), 1) for i in range(8)]


def f(a, b, s, ss):
    if a % 2 == 1:
        raise BaseException('Test exception')
    print(ss, a, b)
    sleep(s)
    print(ss, a, b, 'finihsed')


def tex(ss):
    for x in range (3):
        l = [(i, 'n' + str(x), 5,ss) for i in range(8)]
        with TEX(max_workers=3) as executor:
            print('tex adding')
            run_f = {executor.submit(f, *attr): attr for attr in l}



s_pool = SessionPool(name='session_pool')
s_pool.start()
#
# comm_queue = s_pool.comm_queue
report1 = s.query(Report).first()
# request1 = s.query(Request).first()
#
# in_queue = Queue()
#
#
# scan1 = s.query(Scan).first()
# scan1_dict = {"servers": list(scan1.servers.keys()), "title": "sccan1"}
# task_create_scan = TaskRequest('post', in_queue, 'http://localhost:5000/api/v1.0/scans', dict({'json': scan1_dict}))
#
#
# task_get_scan = TaskRequest('get', in_queue, 'http://localhost:5000/api/v1.0/scans/6', dict({'json': scan1_dict}))
#
#
# report1 = s.query(Report).first()
report1_dict = {"servers": list(report1.servers.keys()), "title": "sccan1"}
# task_create_report = TaskRequest('post', in_queue, 'http://localhost:5000/api/v1.0/reports', dict({'json': report1_dict}))
#
#
# task_get_report = TaskRequest('get', 'http://localhost:5000/api/v1.0/reports/3')
# task_get_report1 = TaskRequest('get', in_queue, 'tp://localhost:5000/api/v1.0/reports/3', dict({'json': report1_dict}))
def put_task(task):
    s_pool = SessionPool(name='session_pool')
    s_pool.start()

    comm_queue = s_pool.comm_queue

    in_queue = Queue()
    comm_queue.put(task)
    response =  in_queue.get()
    return response


def test_request(i):
    # req = Request(title='req test',ip='10.0.1.3,20.0.1.3,20.0.2.1,30.0.1.3,10.0.2.3', owner='null_user')
    for i in range(i):
        req = Request(title='req{} test'.format(i), ip='10.0.1.1,10.0.1.2,10.0.1.3,20.0.1.1,20.0.1.2,20.0.1.3,30.0.1.1,30.0.1.2,30.0.1.3,10.0.2.1,10.0.2.2,10.0.2.3,20.0.2.1,20.0.2.2,20.0.2.3,30.0.2.1,30.0.2.2,30.0.2.3', owner='null_user')
        s.add(req)
    s.commit()
    # process_request(req.id)
    return req

from rq import Queue
from redis import Redis
import time
