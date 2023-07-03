import logging

from lxml import etree

from lib.XmlFile import XmlFile

_logger = logging.getLogger(__name__)


class EncryptModule(XmlFile):

    def keystore(self, key: str):
        entries = self._xml.xpath(f'/properties/entry[@key="{key}"]')
        if entries:
            _logger.debug(f'Found {key} in {self.file}')
            return entries[0].text
        return None

    def add_country(self, country: str, Issuer: str, SN: int):
        _logger.debug(f'Adding {country} {Issuer} {SN} to {self.file}')
        root = self._xml.getroot()
        etree.SubElement(root, 'entry', attrib={'key': f'responseToPointIssuer.{country}'}).text = Issuer
        etree.SubElement(root, 'entry', attrib={'key': f'responseToPointSerialNumber.{country}'}).text = f'{SN:x}'
        _logger.info(f'Added {country} to {self.file}')
        return self
