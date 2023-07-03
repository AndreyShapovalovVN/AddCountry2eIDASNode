import logging
from os import path

from lib.XmlFile import XmlFile

_logger = logging.getLogger(__name__)


class KeyStore(XmlFile):
    """Parsing configuration file for the keystore"""

    def _keystore(self, key: str) -> str | None:
        """Search for key in the configuration file"""
        entries = self.xml.xpath(f'/properties/entry[@key="{key}"]')
        if entries:
            _logger.debug(f'Found {key} in {self.file}')
            return entries[0].text
        _logger.warning(f'Could not find {key} in {self.file}')
        return None

    def get_file(self, key: str) -> str | None:
        """Return the filename to the Keystore"""
        _logger.debug(f'Looking for {key} in {self.file}')
        file = self._keystore(key)
        _logger.debug(f'Found {file} in {self.file}')
        if not file:
            return None
        file = file.replace('..', './eIDAS-conf')
        if not path.isfile(file):
            raise FileNotFoundError(f'Could not find {file}')
        return file

    def get_password(self, key: str) -> str | None:
        """Return the password to the Keystore"""
        return self._keystore(key) if self._keystore(key) else None
