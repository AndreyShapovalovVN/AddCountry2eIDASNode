# Autor: Andrii Shapovalov
# Company: eGA
# Date: 2023-07-19
# Description: Read the XML file from a remote URL
import logging

import requests
from cryptography import x509
from lxml import etree

_logger = logging.getLogger(__name__)


class GetCert:
    """Get the certificate from the XML file"""
    def __init__(self, content: bytes):
        """Read the XML file"""
        self._xml = etree.fromstring(content)
        self.namespace = {'ds': 'http://www.w3.org/2000/09/xmldsig#', 'md': 'urn:oasis:names:tc:SAML:2.0:metadata'}
        _logger.debug(f'XML namespace: {self.namespace}')

    @property
    def is_idp_or_sp(self) -> str:
        """Return the type of the node"""
        _logger.debug(f'is_idp_or_sp: ST - {self._sp()}, iDP - {self._idp()}')
        return 'servise' if self._idp() else 'Connector' if self._sp() else None

    def _find_element(self, path: str) -> etree.Element:
        """Find the element in the XML file"""
        elements = self._xml.findall(path, namespaces=self.namespace)
        return elements[0] if elements else None

    def _sp(self) -> etree.Element:
        """Find the Descriptor element in the XML file"""
        return self._find_element('.//md:SPSSODescriptor')

    def _idp(self) -> etree.Element:
        """Find the Descriptor element in the XML file"""
        return self._find_element('.//md:IDPSSODescriptor')

    def get_signature_key_info(self) -> etree.Element:
        """Return key_info from the signature"""
        signature = self._find_element('.//ds:Signature')
        return signature.find('.//ds:KeyInfo', namespaces=self.namespace)

    def get_descriptor_key_info(self, use: str) -> etree.Element:
        """Return key_info from the descriptor"""
        descriptor = self._sp() or self._idp()
        key_descriptor = descriptor.find(f'.//md:KeyDescriptor[@use="{use}"]', namespaces=self.namespace)
        return key_descriptor.find('.//ds:KeyInfo', namespaces=self.namespace)

    def get_certificate(self, key_info: etree.Element) -> list[x509.Certificate]:
        """Return the certificate from the key_info"""
        x509_data = key_info.find('.//ds:X509Data', namespaces=self.namespace)
        certificates = []
        for x509_certificate in x509_data.findall('.//ds:X509Certificate', namespaces=self.namespace):
            pem = f'-----BEGIN CERTIFICATE-----\n{x509_certificate.text}\n-----END CERTIFICATE-----\n'
            certificates.append(x509.load_pem_x509_certificate(pem.encode('utf-8')))
        if certificates:
            return certificates
        raise Exception('No key_info found')


class RemoteNode:
    """Read the XML file from a remote URL"""
    def __init__(self, url: str):
        """Read the XML file"""
        self.url = url
        response = requests.get(url, verify=False)
        if response.status_code != 200:
            raise Exception(f'Got {response.status_code} from {url}')
        self._xml = GetCert(response.content)

    @property
    def xml(self):
        """Return the XML file"""
        return self._xml

    @property
    def get_encryption_cert(self) -> list[x509.Certificate]:
        """Return the encryption certificate"""
        return self.xml.get_certificate(self.xml.get_descriptor_key_info('encryption'))

    @property
    def get_signature_cert(self) -> list[x509.Certificate]:
        """Return the signature certificate"""
        return self.xml.get_certificate(self.xml.get_descriptor_key_info('signing'))

    @property
    def get_metadata_cert(self) -> list[x509.Certificate]:
        """Return the metadata certificate"""
        return self.xml.get_certificate(self.xml.get_signature_key_info())
