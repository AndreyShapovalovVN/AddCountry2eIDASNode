import logging
import os
from os import path

from lxml import etree

_logger = logging.getLogger(__name__)


class XmlFile:
    """Base class read for XML files"""

    def __init__(self, file: str):
        """Read the XML file"""

        if not path.isfile(file):
            raise FileNotFoundError(f'File {file} not found')
        parser = etree.XMLParser(remove_blank_text=True)
        self._xml = etree.parse(file, parser)
        self.file = file
        self.path2conf = os.path.dirname(file)

    def save(self):
        """Write the XML file"""
        self._xml.write(self.file, pretty_print=True, encoding='utf-8')
        _logger.debug(f'Wrote {self.file}')

    @property
    def xml(self) -> etree.ElementTree:
        """Return the XML file"""
        return self._xml
