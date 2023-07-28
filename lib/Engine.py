# Autor: Andrii Shapovalov
# Company: eGA
# Date: 2023-07-19
# Description: Parsing configuration file for the engine
import logging
from os import path

from lib.ConfigPatch import ConfigPatch
from lib.XmlFile import XmlFile

_logger = logging.getLogger(__name__)
_config = ConfigPatch()


class Engine(XmlFile):
    """Parsing configuration file for the engine"""
    def __init__(self, file: str = None):
        super().__init__(file or f'{_config.config_pach}/SamlEngine.xml')

    def get_config_file(self, config: str, parametr: str = 'fileConfiguration') -> str | None:
        """Return the filename to the configuration file"""
        _logger.debug(f'Looking for {config} in {self.file}')
        instans = self.xml.xpath(f'/instances/instance[@name="{_config.component}"]')
        if not instans:
            raise Exception(f'Could not find {instans} in {self.file}')
        config = instans[0].xpath(f'.//configuration[@name="{config}"]')
        if not config:
            raise Exception(f'Could not find {config} in {self.file}')
        parametr = config[0].xpath(f'.//parameter[@name="{parametr}"]')
        if not parametr:
            raise Exception(f'Could not find {parametr} in {self.file}')
        _logger.debug(f'Found {parametr[0].attrib["value"]} in {self.file}')
        return path.join(self.path2conf, parametr[0].attrib['value']) if parametr[0].attrib['value'] else None
