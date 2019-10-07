import time
import logging

from concurrent.futures.thread import ThreadPoolExecutor as thr_pool

from session_pool import SessionPool

from hlp.const import status
from qualys.request import get_all_requests, get_new_requests, process_request, update_request_status
from qualys import ScopedSession

"""

"""


logger = logging.getLogger('qualys.controller')
logger.setLevel(logging.DEBUG)

# fh = logging.FileHandler(cfg.DB_LOG_FILE)
# fh.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s', '%Y-%m-%d %H:%M:%S')
# fh.setFormatter(formatter)
# dbLogger.addHandler(fh)

# logger.debug('Reading config file')
# config = configparser.ConfigParser()
# config.read('src/qualys_scan.conf')
# cfg.OPS_DEV_MYSQL_CONF = config['ops-dev.db']


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
                future_to_id[executor.submit(process_request, id)] = id

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

def init_logger() -> None:
    """
    logging initialization

    Returns:

    """
    logger = logging.getLogger('qualys')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('log/qualys_scan.log')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)


if __name__ == "__main__":
    session_pool = SessionPool()
    session_pool.start()
    init_logger()
    main()
