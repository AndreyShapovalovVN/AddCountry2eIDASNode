import logging
from abc import ABC, abstractmethod

from lib.Eidas import Eidas
from lib.EncryptModule import EncryptModule
from lib.EncryptionConf import EncryptionConf
from lib.Engine import Engine
from lib.KeyStore import KeyStore
from lib.KeyTool import KeyTool
from lib.MetadataFetcher import MetadataFetcher
from lib.RemoteNode import RemoteNode

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

#  Сюди дадаємо країни, які хочемо додати
Node = {
   # 'UA': 'https://eidas.id.gov.ua',  # Ukraine
    "AT": 'https://vidp.gv.at',  # Austria
    "EE": 'https://eidastest.eesti.ee',  # Estonia
    'CA': 'https://ec2-108-128-3-247.eu-west-1.compute.amazonaws.com',  # EU
}

saml_engine = Engine('./eIDAS-conf/tomcat/SamlEngine.xml')


class Url2Metadata:
    def __init__(self, url):
        self._url = url

    @property
    def service(self) -> str:
        return f'{self._url}/EidasNode/ServiceMetadata'

    @property
    def connector(self) -> str:
        return f'{self._url}/EidasNode/ConnectorMetadata'


def ks_encrypt_connector() -> dict:
    """Return the keystore configuration for the encryption module of the connector"""
    ks = KeyStore(saml_engine.get_config_file('Connector', 'EncryptionConf', 'fileConfiguration'))
    return {'file': ks.get_file('keyStorePath'), 'password': ks.get_password('keyStorePassword')}


def ks_metadata_connector() -> dict:
    """Return the keystore configuration for the metadata module of the connector"""
    ks = KeyStore(saml_engine.get_config_file('Connector', 'SignatureConf', 'fileConfiguration'))
    return {'file': ks.get_file('metadata.keyStorePath'), 'password': ks.get_password('metadata.keyStorePassword')}


def ks_sign_connector() -> dict:
    """Return the keystore configuration for the signature module of the connector"""
    ks = KeyStore(saml_engine.get_config_file('Connector', 'SignatureConf', 'fileConfiguration'))
    return {'file': ks.get_file('keyStorePath'), 'password': ks.get_password('keyStorePassword')}


def ks_encrypt_service() -> dict:
    """Return the keystore configuration for the encryption module of the service"""
    ks = KeyStore(saml_engine.get_config_file('Service', 'EncryptionConf', 'fileConfiguration'))
    return {'file': ks.get_file('keyStorePath'), 'password': ks.get_password('keyStorePassword')}


def ks_metadata_service() -> dict:
    """Return the keystore configuration for the metadata module of the service"""
    ks = KeyStore(saml_engine.get_config_file('Service', 'SignatureConf', 'fileConfiguration'))
    return {'file': ks.get_file('metadata.keyStorePath'), 'password': ks.get_password('metadata.keyStorePassword')}


def ks_sign_service() -> dict:
    """Return the keystore configuration for the signature module of the service"""
    ks = KeyStore(saml_engine.get_config_file('Service', 'SignatureConf', 'fileConfiguration'))
    return {'file': ks.get_file('keyStorePath'), 'password': ks.get_password('keyStorePassword')}


class EidasConfigurator(ABC):
    def __init__(self, country, url, fetcher, encrypt, conf=None, eidas=None):
        self.node = RemoteNode(url)

        self.url = url
        self.country = country
        self.fetcher = MetadataFetcher(fetcher)
        self.encrypt = EncryptModule(encrypt)
        self.conf = EncryptionConf(conf) if conf else None
        self.eidas = Eidas(eidas) if eidas else None
        self.crt_alias_prefix = f'{self.country}-{self.node.xml.is_idp_or_sp}'

    @abstractmethod
    def add_country(self):
        pass


class ConfigureConnector(EidasConfigurator):

    def add_country(self):
        try:
            self.fetcher.add_url(self.url).write()
        except Exception as e:
            _logger.error(f'Error: {e}')
            return

        KeyTool(**ks_sign_service()).add_key(f'{self.crt_alias_prefix}-meta', self.node.get_metadata_cert)
        KeyTool(**ks_metadata_service()).add_key(f'{self.crt_alias_prefix}-meta', self.node.get_signature_cert)
        KeyTool(**ks_encrypt_connector()).add_key(f'{self.crt_alias_prefix}-encr', self.node.get_encryption_cert)

        self.encrypt.add_country(
            country=self.country,
            Issuer=self.node.get_encryption_cert[0].issuer.rfc4514_string(),
            SN=self.node.get_encryption_cert[0].serial_number
        ).save()


class ConfigureService(EidasConfigurator):

    def add_country(self):
        try:
            self.fetcher.add_url(self.url).write()
        except Exception as e:
            _logger.error(f'Error: {e}')
            return

        self.eidas.add_country(self.country, self.url).save()

        KeyTool(**ks_sign_connector()).add_key(f'{self.crt_alias_prefix}-meta', self.node.get_metadata_cert)
        KeyTool(**ks_metadata_connector()).add_key(f'{self.crt_alias_prefix}-meta', self.node.get_signature_cert)
        KeyTool(**ks_encrypt_connector()).add_key(f'{self.crt_alias_prefix}-encr', self.node.get_encryption_cert)

        self.encrypt.add_country(
            country=self.country,
            Issuer=self.node.get_encryption_cert[0].issuer.rfc4514_string(),
            SN=self.node.get_encryption_cert[0].serial_number
        ).save()

        self.conf.add_country(self.country).save()


if __name__ == '__main__':

    for country, url in Node.items():
        '''Configure the connector'''
        _logger.info(f'Configuring {country} connector')
        connector_params = {
            'country': country,
            'url': Url2Metadata(url).connector,
            'fetcher': './eIDAS-conf/tomcat/metadata/MetadataFetcher_Service.properties',
            'encrypt': saml_engine.get_config_file('Service', 'EncryptionConf', 'fileConfiguration'),
        }

        '''Configure the service'''
        _logger.info(f'Configuring {country} service')
        service_params = {
            'country': country,
            'url': Url2Metadata(url).service,
            'fetcher': './eIDAS-conf/tomcat/metadata/MetadataFetcher_Connector.properties',
            'encrypt': saml_engine.get_config_file('Connector', 'EncryptionConf', 'fileConfiguration'),
            'conf': './eIDAS-conf/tomcat/encryptionConf.xml',
            'eidas': './eIDAS-conf/tomcat/eidas.xml'
        }
        ConfigureService(**service_params).add_country()
        ConfigureConnector(**connector_params).add_country()
