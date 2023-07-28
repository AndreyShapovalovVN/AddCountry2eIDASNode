# Autor: Andrii Shapovalov
# Company: eGA
# Date: 2023-07-19
# Description: Parsing configuration file for the engine
import logging

from lib.ConfigPatch import ConfigPatch
from lib.Eidas import Eidas
from lib.EncryptModule import EncryptModule
from lib.EncryptionConf import EncryptionConf
from lib.Engine import Engine
from lib.KeyStore import KS
from lib.KeyTool import KeyTool
from lib.MetadataFetcher import MetadataFetcher
from lib.RemoteNode import RemoteNode

_logger = logging.getLogger(__name__)

config = ConfigPatch()
'''Встановлюємо конфігурацію'''
config.node_version = '2.7'  # Version eIDAS node
config.component = None  # Connector or Service
# config.url = None  # Base URL remote eIDAS node for example: https://eidas.id.gov.ua
config.config_pach = f'/home/andrey/eIdas/2.7/'

#  Сюди дадаємо країни, які хочемо додати
Node = [
    # 'UA': 'https://eidas.id.gov.ua',  # Ukraine
    {'country': "AT", 'url': 'https://vidp.gv.at', 'version': '2.6'},  # Austria
    {'country': "EE", 'url': 'https://eidastest.eesti.ee', 'version': '2.6'},  # Estonia
    {'country': 'CA', 'url': 'https://ec2-108-128-3-247.eu-west-1.compute.amazonaws.com', 'version': '2.6'},  # EU
]


class EidasConfigurator:
    """Class for eIDAS node configuration"""

    def __init__(self, country, url, fetcher, encrypt, conf=None, eidas=None):
        self.node = RemoteNode(url)

        self.url = url
        self.country = country
        self.fetcher = MetadataFetcher(fetcher)
        self.encrypt = EncryptModule(encrypt)
        self.conf = EncryptionConf(conf)
        self.eidas = Eidas(eidas)
        self.ks = KS()
        self.crt_alias_prefix = f'{self.country}-{self.node.xml.is_idp_or_sp}'

    def add_country(self):
        """Add country to eIDAS node"""
        try:
            self.fetcher.add_url(self.url).write()
        except Exception as e:
            _logger.error(f'Error: {e}')
            return

        KeyTool(**self.ks.get_keystor('Metadata')).add_key(f'{self.crt_alias_prefix}-meta', self.node.get_metadata_cert)
        KeyTool(**self.ks.get_keystor('Signature')).add_key(f'{self.crt_alias_prefix}-sign',
                                                            self.node.get_signature_cert)
        KeyTool(**self.ks.get_keystor('Encryption')).add_key(f'{self.crt_alias_prefix}-encr',
                                                             self.node.get_encryption_cert)

        self.encrypt.add_country(
            country=self.country,
            Issuer=self.node.get_encryption_cert[0].issuer.rfc4514_string(),
            SN=self.node.get_encryption_cert[0].serial_number
        ).save()


_logger.setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
# _logger.addHandler(handler)

if __name__ == '__main__':
    '''Configure the logger'''
    # _logger = logging.getLogger(__name__)

    '''Configure the SAML engine'''
    config.node_version = '2.7'
    config.remote_node_version = '2.6'

    for country in Node:
        '''Configure the Connector'''
        _logger.info(f'Configuring {country.get("country")} Connector')

        for compnent in ('Service', 'Connector'):
            config.component = compnent
            config.remote_node_version = country.get('version')
            config.url = country.get("url")
            '''/home/andrey/eIDAS/2.7/Service/eIDAS-conf/tomcat/Service'''
            config.config_pach = f'/home/andrey/eIDAS/2.7/{config.component}/eIDAS-conf/tomcat'

            params = {
                'country': country,
                'url': config.url,
                'fetcher': f'{config.config_pach}/metadata/MetadataFetcher_{config.component}.properties',
                'encrypt': Engine().get_config_file('EncryptionConf', 'fileConfiguration'),
                'conf': f'{config.config_pach}/encryptionConf.xml',
                'eidas': f'{config.config_pach}/eidas.xml'
            }
            EidasConfigurator(**params).add_country()
            config.remote_node_version = '2.6'
