# Autor: Andrii Shapovalov
# Company: eGA
# Date: 2023-07-19
# Description: Parsing configuration file for the keystore
import logging
import re
from os import path

from lib.ConfigPatch import ConfigPatch
from lib.Engine import Engine
from lib.XmlFile import XmlFile

_logger = logging.getLogger(__name__)
_config = ConfigPatch()


class KeyStore(XmlFile):
    """Parsing configuration file for the keystore"""

    def __init__(self, file: str):
        super().__init__(file)

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
        file = re.sub(r'^\.{1,2}', _config.config_pach, file)
        if not path.isfile(file):
            _logger.error(f'Could not find {file} and {_config.config_pach}')
            raise FileNotFoundError(f'Could not find {file}')
        return file

    def get_password(self, key: str) -> str | None:
        """Return the password to the Keystore"""
        return self._keystore(key) if self._keystore(key) else None


class KS:
    def __init__(self):
        self.KEYSTOR = {'Metadata': {"file": None, "password": None},
                        'Signature': {"file": None, "password": None},
                        'Encryption': {"file": None, "password": None}}

        for keystor in self.KEYSTOR.keys():
            if keystor == 'Metadate':
                _ks = KeyStore(Engine().get_config_file('SignatureConf', 'fileConfiguration'))
                self.KEYSTOR[keystor]['file'] = _ks.get_file('metadata.keyStorePath')
                self.KEYSTOR[keystor]['password'] = _ks.get_password('metadata.keyStorePassword')
            elif keystor == 'Signature':
                _ks = KeyStore(Engine().get_config_file('SignatureConf', 'fileConfiguration'))
                self.KEYSTOR[keystor]['file'] = _ks.get_file('keyStorePath')
                self.KEYSTOR[keystor]['password'] = _ks.get_password('keyStorePassword')
            elif keystor == 'Encryption':
                _ks = KeyStore(Engine().get_config_file('EncryptionConf', 'fileConfiguration'))
                self.KEYSTOR[keystor]['file'] = _ks.get_file('keyStorePath')
                self.KEYSTOR[keystor]['password'] = _ks.get_password('keyStorePassword')

    def get_keystor(self, keystor: str) -> dict | None:
        """Return the filename and password to the Keystore"""
        if keystor in self.KEYSTOR.keys():
            return self.KEYSTOR[keystor]
        return None
