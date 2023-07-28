# Autor: Andrii Shapovalov
# Company: eGA
# Date: 2023-07-19
# Description: Parsing configuration file for the EncryptModule
import logging

from lxml import etree

from lib.ConfigPatch import ConfigPatch
from lib.XmlFile import XmlFile

_logger = logging.getLogger(__name__)
_config = ConfigPatch()


class EncryptModule(XmlFile):
    """Parsing configuration file for the EncryptModule"""

    def keystore(self, key: str) -> str | None:
        """Search for keystore in the configuration file"""
        entries = self._xml.xpath(f'/properties/entry[@key="{key}"]')
        if entries:
            _logger.debug(f'Found {key} in {self.file}')
            return entries[0].text
        return None

    def add_country(self, country: str, Issuer: str, SN: int):
        """Add country to the EncryptModule configuration file"""
        if _config.component == 'Service':
            _logger.info(f"You don't need to add information from cerificate to the Service.")
            return self

        _logger.debug(f'Adding {country} {Issuer} {SN} to {self.file}')
        root = self._xml.getroot()
        etree.SubElement(root, 'entry', attrib={'key': f'responseToPointIssuer.{country}'}).text = Issuer
        etree.SubElement(root, 'entry', attrib={'key': f'responseToPointSerialNumber.{country}'}).text = f'{SN:x}'
        _logger.info(f'Added {country} to {self.file}')
        return self
