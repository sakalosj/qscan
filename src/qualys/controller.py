import os
import time
import logging

import configparser
from concurrent.futures.thread import ThreadPoolExecutor as thr_pool

from session_pool import SessionPool

from qualys.request import get_all_requests, get_new_requests, process_request
from qualys import cfg, ScopedSession

"""

"""


logger = logging.getLogger('qualys.controller')
logger.setLevel(logging.DEBUG)

# fh = logging.FileHandler(cfg.DB_LOG_FILE)
# fh.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s', '%Y-%m-%d %H:%M:%S')
# fh.setFormatter(formatter)
# dbLogger.addHandler(fh)

logger.debug('Reading config file')
config = configparser.ConfigParser()
config.read('src/qualys_scan.conf')
cfg.OPS_DEV_MYSQL_CONF = config['ops-dev.db']

def main():
    session = ScopedSession()
    request_set = get_all_requests(session)
    logger.info('Initial requests to process not(failed|finished):{}'.format(request_set))

    with thr_pool(max_workers=5) as executor:
        future_to_id ={}

        while True:
            try:
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
                    except BaseException:
                        # maybe set request to failed
                        logger.error('request {} failed'.format(id))
                    else:
                        logger.info('request {} thread finished correctly'.format(id))
                    finally:
                        future_to_id.pop(future)
                request_set.clear()
            except Exception as e:
                print(e)
                raise
            time.sleep(5)

def init_logger():
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
