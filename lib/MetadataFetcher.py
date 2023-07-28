# Autor: Andrii Shapovalov
# Company: eGA
# Date: 2023-07-19
# Description: Add URL to the metadata whitelist
import logging

from lib.ConfigPatch import ConfigPatch

_logger = logging.getLogger(__name__)
_config = ConfigPatch()


class MetadataFetcher:
    """Add URL to the metadata whitelist"""

    def __init__(self, file: str):
        """Read the file"""
        self.file = file or f'{_config.config_pach}/metadata/MetadataFetcher_{_config.component}.properties'
        with open(self.file, 'r') as f:
            self._content = f.readlines()

    def add_url(self, url: str):
        """Add URL to the metadata whitelist"""
        for i, line in enumerate(self._content):
            vereable, value = line.strip().split('=')
            if vereable == 'metadata.location.whitelist':
                urls = value.split(';')
                if url in urls:
                    raise Exception('URL already in file')
                urls.append(url)
                new_value = ';'.join(urls)
                self._content[i] = f'{vereable}={new_value}\n'
                _logger.info(f'Added {url} to {self.file}')
        return self

    def write(self):
        """Write the file"""
        with open(self.file, 'w') as f:
            f.writelines(self._content)
            _logger.debug(f'Wrote {self.file}')
