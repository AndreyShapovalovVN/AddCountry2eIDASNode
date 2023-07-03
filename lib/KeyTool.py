import logging
import subprocess
import tempfile

import jks
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding

_logger = logging.getLogger(__name__)


class KeyTool:
    """Wrapper for the keytool command"""
    def __init__(self, file: str, password: str):
        self.file = file
        self.password = password
        self._keystore = jks.KeyStore.load(file, password)
        _logger.debug(f'Loading {file}')

    def list_keys(self) -> list[dict[str, x509.Certificate]]:
        """Return a list of all certificates in the keystore"""
        crts = list()
        for alias, certificate in self._keystore.certs.items():
            crt = {alias: x509.load_der_x509_certificate(certificate.cert, None)}
            crts.append(crt)
            _logger.debug(f'{alias} - {crt[alias].serial_number}; {crt[alias].subject.rfc4514_string()}')
        return crts

    def check_cert(self, alias: str, certificate: x509.Certificate) -> bool:
        for crt in self.list_keys():
            if alias in crt:
                if crt[alias].serial_number == certificate.serial_number:
                    _logger.debug(f'Found {alias} in {self.file}')
                    return True
        _logger.warning(f'Could not find {alias} in {self.file}')
        return False

    def delete_cert(self, alias: str):
        """Delete a certificate from the keystore"""
        command = [
            'keytool',
            '-delete',
            '-alias', alias,
            '-keystore', self.file,
            '-storepass', self.password,
            '-noprompt',
        ]
        p = subprocess.run(command, capture_output=True, text=True)
        _logger.debug(f'Executed {p}')
        _logger.info(f'Deleted {alias} from {self.file} {p.returncode}')
        return self

    def clear(self):
        for c in self.list_keys():
            for k in c.keys():
                self.delete_cert(k)
        return self

    def add_key(self, alias: str, certificate: list[x509.Certificate]):
        """Add a certificate to the keystore"""
        self.delete_cert(alias)

        pem = ''
        for c in certificate:
            pem += f'{c.public_bytes(Encoding.PEM).decode("utf-8")}'

        with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
            f.write(pem)
            f.flush()
            _logger.debug(f'Wrote {f.name}')
            command = [
                'keytool',
                '-importcert',
                '-alias', alias,
                '-file', f.name,
                '-keystore', self.file,
                '-storepass', self.password,
                '-noprompt',
            ]
            p = subprocess.run(command, capture_output=True, text=True)
            _logger.debug(f'Executed {p}')
        _logger.info(f'Added {alias} to {self.file} {p.returncode}')
        return self
