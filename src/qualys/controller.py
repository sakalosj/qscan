import time
import logging

from concurrent.futures.thread import ThreadPoolExecutor as thr_pool

from redis import Redis
from rq import Queue

from hlp.cfg import LOG_FILE, REDIS_HOST, QS_DB_URI
from hlp.const import status
from qualys.db import ScopedSession, init_db
from qualys.request import get_all_requests, get_new_requests, process_request, update_request_status



logger = logging.getLogger('controller')
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

redis_conn = Redis(REDIS_HOST, 6379)
redis_queue = Queue(connection=redis_conn)  # no args implies the default queue


def main() -> None:
    """
    Main function responsible for basic application flow

    Returns:
        None

    """
    session = ScopedSession()
    request_set = get_all_requests(session)
    session.commit()
    logger.info('Initial requests to process not(failed|finished):{}'.format(request_set))

    with thr_pool(max_workers=5, thread_name_prefix='main_thrpool') as executor:
        future_to_id = {}

        while True:
            session.commit()
            new_requests = get_new_requests(session)
            logger.info('processing new requests {}'.format(new_requests))
            request_set.update(new_requests)
            for id in request_set:
                if id in future_to_id.values():
                    logger.info('request id is allready processing in thread')
                    continue

                logger.debug('starting thread for request {}'.format(id))
                future_to_id[executor.submit(process_request,redis_queue, id)] = id

            logger.info('processing threads in future_to_id:{}'.format(future_to_id))
            done = [future_id for future_id in future_to_id.items() if future_id[0].done()]
            logger.info('threads done: {}'.format(done))
            for future, id in done:
                try:
                    future.result()
                except Exception:
                    logger.exception('request {} raised exception'.format(id))
                    update_request_status(id, status['FAILED'], session)
                    session.commit()
                else:
                    logger.info('request {} thread finished without excception'.format(id))
                finally:
                    future_to_id.pop(future)
            request_set.clear()

            time.sleep(5)


if __name__ == "__main__":
    init_db(QS_DB_URI)
    main()
