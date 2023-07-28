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


class EncryptionConf(XmlFile):

    def __init__(self, file: str = None):
        self.config = ConfigPatch()
        super().__init__(file or f'{_config.config_pach}/encryptionConf.xml')

    def add_country(self, country: str):
        root = self._xml.getroot()
        etree.SubElement(root, 'entry', attrib={'key': f'EncryptTo.{country}'}).text = 'true'
        _logger.info(f'Added {country} to encryptionConf.xml')
        return self
