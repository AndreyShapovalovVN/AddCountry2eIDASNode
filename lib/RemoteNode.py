import logging
from typing import cast

import requests
from cryptography import x509
from lxml import etree
from lxml.etree import _Element

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
        if self._idp():
            return 'servise'
        if self._sp():
            return 'connector'
        raise ValueError('Could not identify node type from metadata')

    @staticmethod
    def _require_element(element: _Element | None, message: str) -> _Element:
        if element is None:
            raise ValueError(message)
        return element

    def _find_element(self, path: str) -> _Element | None:
        """Find the element in the XML file"""
        elements = cast(list[_Element], self._xml.findall(path, namespaces=self.namespace))
        return elements[0] if elements else None

    def _sp(self) -> _Element | None:
        """Find the Descriptor element in the XML file"""
        return self._find_element('.//md:SPSSODescriptor')

    def _idp(self) -> _Element | None:
        """Find the Descriptor element in the XML file"""
        return self._find_element('.//md:IDPSSODescriptor')

    def get_signature_key_info(self) -> _Element:
        """Return key_info from the signature"""
        signature = self._require_element(self._find_element('.//ds:Signature'), 'Signature not found in metadata')
        key_info = signature.find('.//ds:KeyInfo', namespaces=self.namespace)
        return self._require_element(key_info, 'Signature KeyInfo not found in metadata')

    def get_descriptor_key_info(self, use: str) -> _Element:
        """Return key_info from the descriptor"""
        descriptor = self._require_element(self._sp() or self._idp(), 'Descriptor not found in metadata')
        key_descriptor = descriptor.find(f'.//md:KeyDescriptor[@use="{use}"]', namespaces=self.namespace)
        required_key_descriptor = self._require_element(key_descriptor, f'KeyDescriptor use="{use}" not found')
        key_info = required_key_descriptor.find('.//ds:KeyInfo', namespaces=self.namespace)
        return self._require_element(key_info, f'KeyInfo for use="{use}" not found')

    def get_certificate(self, key_info: _Element) -> list[x509.Certificate]:
        """Return the certificate from the key_info"""
        x509_data = self._require_element(key_info.find('.//ds:X509Data', namespaces=self.namespace), 'X509Data not found')
        certificates = []
        for x509_certificate in x509_data.findall('.//ds:X509Certificate', namespaces=self.namespace):
            if not x509_certificate.text:
                raise ValueError('X509Certificate entry is empty')
            pem = f'-----BEGIN CERTIFICATE-----\n{x509_certificate.text}\n-----END CERTIFICATE-----\n'
            certificates.append(x509.load_pem_x509_certificate(pem.encode('utf-8')))
        if certificates:
            return certificates
        raise ValueError('No certificates found')


class RemoteNode:
    """Read the XML file from a remote URL"""
    def __init__(self, url: str):
        """Read the XML file"""
        self.url = url
        response = requests.get(url, verify=False)
        if response.status_code != 200:
            raise ValueError(f'Got {response.status_code} from {url}')
        self._xml = GetCert(response.content)

    @property
    def xml(self) -> GetCert:
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
