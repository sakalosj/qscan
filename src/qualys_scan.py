#!/usr/bin/python3
import os
import sys
import re
import time
import logging
import socket
import argparse
import signal
import subprocess
import configparser

from qualys.controller import QualysController

# TODO signal handling - to be able to change debug level on fly
config = configparser.ConfigParser()
config.read('qualys_scan.conf')
logger = logging.getLogger('qualys')
logger.setLevel(logging.DEBUG)
logfile = os.path.join(config['qualys']['logDir'], 'qualys_scan.log')
fh = logging.FileHandler(logfile)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

PID_FILE = 'qualys_scan.pid'


def uncaughtExceptionLogger(exc_type, exc_value, exc_traceback):
    """Function to process uncaught exceptions via logger"""
    logger.critical("Uncaught exception occurred:", exc_info=(exc_type, exc_value, exc_traceback))
    exit(255)


sys.excepthook = uncaughtExceptionLogger  # Hook to process uncaught exceptions via logger


def getLock(lockName: str) -> bool:
    """
    This function handles socket lock and tests if lock exist.

    Returns:
        True if was able to get lock (lock was free)
        False if was not able to get lock (lock exist)
    """

    getLock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        getLock._lock_socket.bind('\0' + lockName)
        logger.debug('Lock acquired')
        return True
    except socket.error:
        logger.debug('Lock exists')
        return False


def createPidFile(pidFile: str) -> None:  # TODO ??? remove hardcoded filename
    """Function to create pidfile"""
    try:
        with open(pidFile, 'w') as pfile:
            pfile.write(str(os.getpid()))
    except OSError:
        logger.exception('Failed to create PID file {}'.format(pidFile))
        exit(112)


def readPidFile(pidFile: str) -> str:
    """Read pidfile and return PID"""
    logger.debug('Reading PID file {}'.format(pidFile))
    try:
        with open(pidFile) as pfile:
            pid = pfile.read()
        return pid
    except OSError:
        logger.exception("PID read failed")
        exit(112)


def deletePidFile(pidFile: str) -> None:
    """Function to delete pidfile"""
    logger.debug('Removing PID file')
    try:
        os.remove(pidFile)
    except OSError:
        logger.exception('Unable to remove PID file {}'.format(pidFile))
        exit(113)


def checkPid(PID: str, procName: str) -> bool:  # TODO !!!!!!!!!!!!!! NEED TESTING !!!!!!!!!!!!!
    """
    Check if process with PID contains string procName

    Args:
        PID: os process id
        procName: os process name

    Returns:
        bool: True if process contains procName string, else False
    """
    p = subprocess.Popen(["ps -o cmd= {}".format(PID)], stdout=subprocess.PIPE, shell=True)
    psOutput = p.communicate()[0]

    if re.compile('.*{}.*'.format(procName)).search(psOutput.decode('utf-8')) is None:
        return False
    else:
        return True


def start():
    """
    Function is checking if any instance of program is running and start QualysController in background
    """
    logger.debug('Starting qualys_scan')
    if not getLock('qualys'):
        exit(101)  # TODO??? log exit codes
    logger.removeHandler(ch)
    controller = QualysController()
    runInBackground(controller.main)
    time.sleep(5)
    pid = readPidFile(PID_FILE)
    if not checkPid(pid, 'qualys_scan.py'):
        exit(102)


def stop():  # todo check if pid is really qualys scan
    """
    Function stops running instance of qualys_scan.py

    Returns:

    """
    logger.debug('Stopping of qualys_scan initiated ...')
    if getLock('qualys'):
        logger.warning('qualys_scan is not running')
        exit(111)
    pid = readPidFile(PID_FILE)
    if not checkPid(pid, 'qualys_scan.py'):
        logger.warning('PID {} doesnt look like qualys_scan.py - Please stop manually')  # TODO: signal handling to gracefull stopping
        exit(112)
    logger.debug('PID : {}'.format(pid))
    os.kill(int(pid), signal.SIGTERM)
    time.sleep(1)

    try:  # Check if the process that we killed is alive.
        os.kill(int(pid), 0)
        logger.debug('Kill failed')
        raise Exception("""wasn't able to kill the process 
                          HINT:use signal.SIGKILL or signal.SIGABORT""")
    except OSError:  # Exception that process doesnt exist - we can remove pid file
        logger.debug('Process killed ')
    logger.debug('Removing pid file')
    deletePidFile(PID_FILE)


def status():
    # TODO add more sophisticated check to identify if is not hung (logfile watch?)
    if getLock('qualys'):
        logger.debug('qualys_scan is not running')
        exit(111)
    logger.debug('qualys_scan is running')
    exit(0)


def reload():
    pass


def runInBackground(func):
    """
    Daemonize class. UNIX double fork mechanism.
    """
    logger.debug("runInBackground function started")
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            # sys.exit(0)
            return
    except OSError as err:
        logger.error('fork #1 failed: {}'.format(err))
        sys.exit(1)

    # decouple from parent environment
    # os.chdir('/')
    os.setsid()
    os.umask(0)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent
            sys.exit(0)
    except OSError as err:
        logger.error('fork #2 failed: {}'.format(err))
        sys.exit(1)

    # redirect standard file descriptors
    # sys.stdout.flush()
    # sys.stderr.flush()
    # si = open(os.devnull, 'r')
    # so = open(os.devnull, 'a+')
    # se = open(os.devnull, 'a+')
    #
    # os.dup2(si.fileno(), sys.stdin.fileno())
    # os.dup2(so.fileno(), sys.stdout.fileno())
    # os.dup2(se.fileno(), sys.stderr.fileno())
    createPidFile(PID_FILE)
    func()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='qualys daemon usage')
    parser.add_argument('action', choices=['start', 'stop', 'status'])
    parser.add_argument('-s', '--silent', help='silent mode - no output to terminal', action='store_true')
    args = vars(parser.parse_args())
    print(args)
    if args['silent']:
        logger.removeHandler(ch)

    if args['action'] == 'start':
        start()

    if args['action'] == 'stop':
        stop()

    if args['action'] == 'status':
        status()
