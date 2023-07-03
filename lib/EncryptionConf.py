import logging

from lxml import etree

from lib.XmlFile import XmlFile

_logger = logging.getLogger(__name__)


class EncryptionConf(XmlFile):

    def add_country(self, country: str):
        root = self._xml.getroot()
        etree.SubElement(root, 'entry', attrib={'key': f'EncryptTo.{country}'}).text = 'true'
        _logger.info(f'Added {country} to encryptionConf.xml')
        return self
