import logging
from os import path
from typing import cast

from lxml.etree import _Element
from lib.XmlFile import XmlFile

_logger = logging.getLogger(__name__)


class Engine(XmlFile):
    def get_config_file(self, instans: str, config: str, parametr: str) -> str:
        """Return the filename to the configuration file"""
        _logger.debug(f'Looking for {config} in {self.file}')
        instances = cast(list[_Element], self.xml.xpath(f'/instances/instance[@name="{instans}"]'))
        if not instances:
            raise ValueError(f'Could not find instance {instans} in {self.file}')

        configurations = cast(list[_Element], instances[0].xpath(f'.//configuration[@name="{config}"]'))
        if not configurations:
            raise ValueError(f'Could not find configuration {config} in {self.file}')

        parameters = cast(list[_Element], configurations[0].xpath(f'.//parameter[@name="{parametr}"]'))
        if not parameters:
            raise ValueError(f'Could not find parameter {parametr} in {self.file}')

        value = parameters[0].attrib.get('value')
        if not value:
            raise ValueError(f'Empty parameter value for {parametr} in {self.file}')

        _logger.debug(f'Found {value} in {self.file}')
        return path.join(self.path2conf, value)
