#!/bin/bash
#
# qualys_scan.sh      Startup script for qualys_scan.py
#
# chkconfig: 345 83 7
# description: qualys_scan init script
# config: qualys_scan.conf
# pidfile: qualys_scan.pid
#
### BEGIN INIT INFO
# Provides: qualys_scan daemon
# Required-Start: $local_fs $network
# Required-Stop: $local_fs
# Short-Description: Manage execution of qualys_scan
# Description: qualys_scan is backend application to perform qualys scans and reports and store result in database.
### END INIT INFO

# Source function library.
. /etc/rc.d/init.d/functions

# teradata odbs driver config
export ODBCINI=/automation/QualysScan/odbc.ini

DIR=/automation/QualysScan/
CMD=qualys_scan.py
PROG=qualys_scan
USER=qualysscan
RETVAL=0

start() {
        echo -n $"Starting $PROG"
        su - $USER -c "cd $DIR;./$CMD start -s" 2>&1 1>/dev/null
        RETVAL=$?
        if [ $RETVAL = 0 ]; then
            success
        elif [ $RETVAL = 101 ]; then
            echo -en "\nLock detected - $PROG already running" && failure
        elif [ $RETVAL = 102 ]; then
            echo -en "\n$PROG was unable to start" && failure
        else
        echo -en "\nUnknown error " && failure
        fi
        echo
        return $RETVAL
}

stop() {
    echo -n $"Stopping $PROG"
    su - $USER -c "cd $DIR;./$CMD stop -s" 2>&1 1>/dev/null
    RETVAL=$?
    if [ $RETVAL = 0 ]; then
        success
    elif [ $RETVAL = 111 ]; then
        echo -en "\n$PROG is not runnig" && failure
    elif [ $RETVAL = 112 ]; then
        echo -en "\nError reading PID file" && failure
    else
        echo -en "\nUnknown error $RETVAL" && failure
    fi
    echo
    return $RETVAL
}

status(){
    echo -en $"Status of $PROG\t\t\t\t\t"
    su - $USER -c "cd $DIR;./$CMD status -s"  2>&1 1>/dev/null
    RETVAL=$?
    [ $RETVAL = 0 ] && echo "[Running]" || echo "[Stopped]"
    return $RETVAL
}

case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  status)
    status
    ;;
  restart)
    stop
    start
    ;;
  *)
    echo $"Usage: $prog {start|stop|restart|status}"
    RETVAL=2
esac

exit $RETVAL
