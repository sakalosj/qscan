import xml.etree.ElementTree as ET
from qualys.error import QualysResponseException, QualysApiException
import logging
import csv

logger = logging.getLogger('qualys.response')


class QualysResponse:
    """
    Class responsible for response parsing

    Correct response have to be in XML format.
    In case response contains API error, XML will contain <CODE> and <TEXT>

    """
    def __init__(self, rawData, data_type='xml'):
        """
        Initialize variables and generates ElementTree instance from it if it was able to parse input data

        Args:
            rawData: http response in string, if everything is ok it should be XML

        TODO: !!!! incorect logic - parse functions shuold be removed from constructor or logic to determine type of
            input have to be implemented !!!!
        """
        self._rawData = rawData
        self.xml = None
        self.csv = None
        self._parseXML()
        self._parseCSV()

    def _parseXML(self):
        try:
            self.xml = ET.fromstring(self._rawData)
            # Checks if response contains API error
            if self.xml.find('.//CODE') is not None:
                raise QualysApiException('QAPI'+self.xml.find('.//CODE').text, self.xml.find('.//TEXT').text)
        except ET.ParseError as e:
            logger.warning('Unable to parse response using xml parser.')
            # logger.exception('Error parsing response\nvalue stored in self.xml:\n{}\nvalue stored in self.xml'.format(e, self.xml))
            # raise QualysResponseException('ElementTree was unable to parse data')

    def _parseCSV(self):
        self.csv


    def test(self):
        """
        Returns ElementTree self.xml in text

        Returns:
            Returns ElementTree self.xml in text

        """
        return ET.dump(self.xml)


