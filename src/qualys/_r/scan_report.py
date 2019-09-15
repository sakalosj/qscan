import threading

from qualys.scan import Scan
from qualys.api import QualysApi
from qualys.db import MysqlApi
from qualys.vulner import Vulner
from qualys.server import Server
from qualys.error import QualysApiException, QualysServerException, error_handling_decorator
import configparser
import re
import logging
import ipaddress

logger = logging.getLogger('qualys.scan_report')

config = configparser.ConfigParser()
config.read('qualys_scan.conf')


class QualysScanReport(threading.Thread):
    """
    Class is responsible for report objects lifecycle and data in qualys_report table.
    """

    def __init__(self, qualysApi: QualysApi, dbConnection: MysqlApi, initData) -> None:
        """
        Initialize variables and execute correct initialization function based on initData type

        Args:
            qualysApi: QualysApi instance used to communicate with QualysGuard
            dbConnection: MysqlApi instance used to communicate with internal DB
            initData: QualysScan instance used as reference for Qualys report
        """

        threading.Thread.__init__(self, daemon=True)
        logger.debug("Initializing QualysScanReport instance")
        self._qualysApi = qualysApi
        self._dbConnection = dbConnection
        self._reportId = None
        self._scanRef = None
        self._status = None
        self._launched = None
        self._size = None
        self._reportDataXml = None
        self._reportDataHeader = {}
        self._apiSection = '/api/2.0/fo/report/'
        self.title = "new report - should be already changed to scan name"
        self._report_type = 'Scan'
        self._echo_request = '0'
        self._template_id = '90993361'
        self._output_format = 'xml'
        self._relatedScan = None

        if isinstance(initData, Scan):
            self.initializeByScanRef(initData)
        if type(initData) is int:
            self.initializeByReportId(initData)

    def setReportId(self, reportId):
        self._reportId = reportId

    @property
    def id(self):
        return self._reportId

    @property
    def status(self):
        """
        str: current status of instance
            setter is updating status in DB
        """
        return self._status

    @status.setter
    def status(self, status):
        logger.debug('Setting report instance status to {} and updating DB'.format(status))
        self._status = status
        self._update()

    @property
    def scanRef(self):
        return self._scanRef

    @error_handling_decorator()
    def initializeByScanRef(self, initData: Scan) -> None:
        """
        Initialize by launching new report using scan reference and creating new entry in qulays_report table

        Args:
            initData (Scan): QualysScan instance reference
        """

        self._relatedScan = initData
        self._scanRef = initData.scanRef
        logger.debug('Initializing report by scan {}'.format(self._relatedScan.id))
        self.title = initData.title
        self.launch()

    @error_handling_decorator()
    def initializeByReportId(self, qualysReportId: int) -> None:
        """
        Initialize instance based on report id in qualys_report table

        Args:
            qualysReportId:  qualys_report id

        """
        # TODO: process all values from db row or change approach
        # TODO: !!!!!!!!!!!!!! implement check if scan ref is not already processed - done on db level - unique added haveto be added on app level too

        self._reportId = qualysReportId
        logger.debug('Initializing report by qualys_report id {}'.format(self._reportId))
        with self._dbConnection.get_cursor() as cursor:
            sql = "SELECT qualys_scan_ref_fk, status FROM qualys_report WHERE id = %s"
            values = self._reportId
            cursor.execute(sql, values)
            result = cursor.fetchone()
            self._dbConnection.commit()
        self._scanRef = result['qualys_scan_ref_fk']
        self._status = result['status']

    @error_handling_decorator()
    def queryMetaData(self) -> None:
        """
        Get status of report via qualys API
        """

        param = {'action': 'list',
                 'id': self._reportId
                 }

        errorCount = 0
        while True:
            """
            Because of delay between report launch request and its visibility via API in QualysGuard, we have to retry list few times with 
            small delay before reporting it as failure
            """
            logger.debug('Checking if report is in API response, try #{}'.format(errorCount + 1))
            response = self._qualysApi.sendRequest(param, self._apiSection)
            if response.xml.find(".//ID") is not None:
                logger.debug('Report found (retry {})'.format(str(errorCount + 1)))
                break
            else:
                errorCount += 1

            if errorCount > 3:
                logger.error('Report id {} not in API reponse'.format(self._reportId))
                break

        # TODO:Validate if output contains report data and raise warning
        try:
            # last character 'Z' discarded to avoid "Out of range value for column at row mysql" warning
            self._launched = response.xml.find(".//LAUNCH_DATETIME").text.rstrip('Z')

            self._size = response.xml.find(".//SIZE").text
            self._status = response.xml.find(".//STATE").text
        except AttributeError:
            logger.warning('Response doesnt contain expected data.')
            self._status = 'Pending_data'
        self._update()

    @error_handling_decorator()
    def launch(self) -> None:
        """
        Launch Qualys report
        """

        reportId = self._isReportAlreadyGenerated()
        if reportId:
            logger.warning('Report for scanref {} already exist, reinitializing instance based on existing record'.format(self._scanRef))

            # set related scan status to Processed should be not required but will  help keep data consistent in case of strange failure
            self._relatedScan.status = 'Processed'

            self.initializeByReportId(reportId)
            return
        logger.debug('Launching new report with reference scan id: {} and scan_ref {}'.format(self._relatedScan.id, self._relatedScan.scan_ref))
        param = {'action': 'launch',
                 'report_refs': self._scanRef,
                 'report_title': self.title,
                 'report_type': self._report_type,
                 'echo_request': self._echo_request,
                 'template_id': self._template_id,
                 'output_format': self._output_format
                 }

        response = self._qualysApi.sendRequest(param, self._apiSection)
        self._reportId = response.xml.find(".//VALUE").text  # TODO !!!!!! add xml error if value not found to @errorHandlingDecorator()
        logger.debug('Report successfully launched')
        self._status = "Requested"
        self._update()

        # scan is changed to Processed only if related report was launched
        if isinstance(self._relatedScan, Scan):
            self._relatedScan.status = 'Processed'

    @error_handling_decorator()
    def _isReportAlreadyGenerated(self) -> None:
        """
        Checks if there is report with corresponding scan_ref in qualys report table
        """
        with self._dbConnection.get_cursor() as cursor:
            sql = "SELECT id FROM qualys_report WHERE qualys_scan_ref_fk = %s"
            cursor.execute(sql, self._scanRef)
            result = cursor.fetchone()
        return False if result is None else result['id']

    def _update(self) -> None:
        """
        Update corresponding row in qualys_report table based on current QualysScanReport instance state
        """
        currentState = {
            'launched': self._launched,
            'size': self._size,
            'status': self._status,
            'qualys_scan_ref_fk': self._scanRef
        }
        logger.debug('Updating report id: {}'.format(self._reportId))

        # building query based on 2 dictionaries: currentState, self._reportDataHeader
        updateList = {k: v for k, v in currentState.items() if v is not None}
        updateList.update(self._reportDataHeader)
        insertList = updateList.copy()
        insertList.update({'id': self._reportId})
        sqlInsert = 'INSERT INTO qualys_report SET {}'.format(', '.join('{}=%s'.format(k) for k in insertList))
        sqlOnUpdate = 'ON DUPLICATE KEY UPDATE {}'.format(', '.join('{}=%s'.format(k) for k in updateList))
        sql = sqlInsert + ' ' + sqlOnUpdate
        values = list(insertList.values()) + list(updateList.values())

        with self._dbConnection.get_cursor() as cursor:
            cursor.execute(sql, values)
            self._dbConnection.commit()

    def download(self) -> None:
        """
        Function to download_report report results
        """

        logger.debug('Downloading report {}'.format(self._reportId))
        apiSection = '/api/2.0/fo/report/'
        param = {
            'action': 'fetch',
            'id': self._reportId,
        }
        response = self._qualysApi.sendRequest(param, apiSection)
        self._reportDataXml = response.xml

    @error_handling_decorator()
    def uploadDataToDb(self):
        """
            Function to upload downloaded report results to database

            Data processing loop logic
            First are processed IPs from report and with value data_ok in table qualys_report2server column qualys_server_status.
            After done notProcessedIPs list is generated.
        """
        # TODO: REWORK TO HAVE AVAILABLE RELATED SCAN SO REQUESTED IP LIST CAN BE USED FOR VALIDATION OF RESULT
        # TODO: IF SERVER HAS NO VULNER HOW WILL BE DISPLAYED IN REPORT?????

        xmlRoot = self._reportDataXml
        logger.debug('uploading report {} data to db'.format(self._reportId))
        #: dict: parsed report result header
        self._reportDataHeader = {
            'user': self._reportDataXml.find('./HEADER/KEY[@value="USERNAME"]').text,
            'datetime': self._reportDataXml.find('./HEADER/KEY[@value="DATE"]').text.rstrip('Z'),
            'title': self._reportDataXml.find('./HEADER/KEY[@value="TITLE"]').text,
            'target': self._reportDataXml.find('./HEADER/KEY[@value="TARGET"]').text,
            'excluded_target': self._reportDataXml.find('./HEADER/KEY[@value="EXCLUDED_TARGET"]').text,
            'duration': self._reportDataXml.find('./HEADER/KEY[@value="DURATION"]').text,
            'scan_host': self._reportDataXml.find('./HEADER/KEY[@value="SCAN_HOST"]').text,
            'host_alive': self._reportDataXml.find('./HEADER/KEY[@value="NBHOST_ALIVE"]').text,
            'host_total': self._reportDataXml.find('./HEADER/KEY[@value="NBHOST_TOTAL"]').text,
            'report_type': self._reportDataXml.find('./HEADER/KEY[@value="REPORT_TYPE"]').text,
            'options': self._reportDataXml.find('./HEADER/KEY[@value="OPTIONS"]').text,
            # 'status':           self._reportDataXml.find('./HEADER/KEY[@value="STATUS"]').text
        }

        processedIPs = [] #: list: to keep track of processed IPs for later check vs requested IPs
        # process ip sections of xml root
        for ip in xmlRoot.findall('./IP'):  # :TODO is possibility that there will be no IP? what wii
            try:
                logger.debug('processing server ip: {}'.format(ip.get("value")))
                server = Server(ip.get("value"))  # TODO: add check if created and continue next iter if not
            except QualysServerException as e:
                logger.error('Error occurred during server parsing: {}, report data will not be complete'.format(e.text))
                continue

            logger.debug('Setting last report {} for server {}'.format(self._reportId, server.ip))
            server.set_last_report(self._reportId)  # TODO add check to test if current report is really newer one
            with self._dbConnection.get_cursor() as cursor:
                sql = "INSERT IGNORE INTO qualys_report2server (id_fk, qualys_server_ip_fk, qualys_server_status) VALUES (%s,%s,%s)"
                values = (self._reportId, server.ip, 'data_ok')
                cursor.execute(sql, values)
                self._dbConnection.commit()
            # process cat sections in ip section
            for cat in ip.findall(".//VULNS/CAT"):
                catString = ''.join(['%s = "%s", ' % (key, value) for (key, value) in cat.items()])[:-2]
                # process vulnerability sections in cat section
                for vuln in cat.findall(".//VULN"):
                    vulnerData = {
                        'vulnerId': vuln.get('number'),
                        'severity': vuln.get('severity'),
                        'cveId': vuln.get('cveid'),
                        'lastUpdate': vuln.find("./LAST_UPDATE").text.rstrip('Z'),
                        'title': vuln.find("./TITLE").text,
                        'solution': vuln.find("./SOLUTION").text
                    }

                    vulner = Vulner(self._qualysApi, self._dbConnection, vulnerData)
                    if not vulner.exist():  # TODO: consider add exist() to naddNew() so no testing is required
                        vulner.addNew()

                    with self._dbConnection.get_cursor() as cursor:
                        sql = '''INSERT INTO qualys_server2vulner
                                        SET qualys_report2server_report_id_fk = %s,
                                        qualys_report2server_server_ip_fk =%s,
                                        qualys_vulner_id_fk = %s,
                                        qualys_cat = %s
                                        ON DUPLICATE KEY UPDATE qualys_cat = concat(IFNULL(qualys_cat,""),%s)
                                        '''
                        cursor.execute(sql, (
                            self._reportId, server.ip, vulnerData['vulnerId'], catString, catString))
                        # TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! concat is appending to qualys_cat on every rerun - have to be handled somehow - not allow
                        self._dbConnection.commit()
            processedIPs.append(server.ip)

        IPregex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        targetIPs = self._reportDataXml.find('./HEADER/KEY[@value="TARGET"]').text.split(',')
        targetIPs = self.__convertMixed2SingleIPs(targetIPs)
        # excludedIPs contains 'N/A' if there is no IP - this value have to be filtered by IPregex in list comprehension
        excludedIPs = self._reportDataXml.find('./HEADER/KEY[@value="EXCLUDED_TARGET"]').text.split(',')
        notProcessedIPs = [ip for ip in targetIPs + excludedIPs if ip not in processedIPs and IPregex.match(ip)]

        for ip in notProcessedIPs:
            try:
                server = Server(ip)  # TODO: add check if creted and continue next iter if not
            except QualysServerException as e:
                print(e.text)
                continue

            server.set_last_report(self._reportId)  # TODO add check to test if current report is really newer one
            sql = "INSERT qualys_report2server SET id_fk = %s, qualys_server_ip_fk  = %s, qualys_server_status = %s " #ON DUPLICATE KEY UPDATE qualys_server_status = %s "
            value = (self._reportId, server.ip, 'no_data')#, 'no_data')
            with self._dbConnection.get_cursor() as cursor:
                cursor.execute(sql, (self._reportId, server.ip, 'no_data'))
                self._dbConnection.commit()

        self._status = 'Processed'
        self._update()

    def __convertMixed2SingleIPs(self, ipList: list) -> list:
        """
        Convert range in list to IP's and validate IPs.

        Note: function is required because QualysGuard is combining consequetive IP's to range ex. 1.1.1.5-1.1.1.9

        Args:
            ipList: list of IP witch can contain also IP range

        Returns:
            None

        """
        newList = []
        for item in ipList:
            # if is IP
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', item):
                # validate item
                ipaddress.IPv4Address(item)
                newList.append(item)
            # if is IP range
            elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', item):
                # validate and convert IP range to list of IP's
                ip0 = ipaddress.IPv4Address(item.split('-')[0])
                ip1 = ipaddress.IPv4Address(item.split('-')[1])
                while ip0 <= ip1:
                    newList.append(str(ip0))
                    ip0 += 1
            else:
                logger.error('{} is not valid IP address'.format(item))
                pass  # raise error that in list is incorrect value
        return newList


