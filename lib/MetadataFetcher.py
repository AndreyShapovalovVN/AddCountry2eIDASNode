import logging

_logger = logging.getLogger(__name__)


class MetadataFetcher:
    def __init__(self, file: str):
        with open(file, 'r') as f:
            self._content = f.readlines()
        self.file = file

    def add_url(self, url: str):
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
        with open(self.file, 'w') as f:
            f.writelines(self._content)
            _logger.debug(f'Wrote {self.file}')
