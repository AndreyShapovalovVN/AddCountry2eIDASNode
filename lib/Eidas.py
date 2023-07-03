import logging
import re

from lib.XmlFile import XmlFile, etree

_logger = logging.getLogger(__name__)


class Eidas(XmlFile):

    @property
    def _count(self):
        i = 0
        for entry in self._xml.xpath('/properties/entry'):
            if re.findall(r'^service\d+\.id$', entry.attrib['key']):
                i += 1
        return i

    @property
    def services(self):
        sn = self.xml.xpath(f'/properties/entry[@key="service.number"]')

        return int(sn[0].text) if len(sn) == 1 else 0

    def add_country(self, country: str, url: str):
        root = self._xml.getroot()
        id = self._count + 1
        etree.SubElement(root, 'entry', attrib={'key': f'service{id}.id'}).text = country
        etree.SubElement(root, 'entry', attrib={'key': f'service{id}.name'}).text = f'{country} proxy_sevice'
        etree.SubElement(root, 'entry', attrib={'key': f'service{id}.skew.notbefore'}).text = '0'
        etree.SubElement(root, 'entry', attrib={'key': f'service{id}.skew.notonorafter'}).text = '0'
        etree.SubElement(root, 'entry', attrib={'key': f'service{id}.metadata.url'}).text = url
        _logger.info(f'Added {country} to {self.file}')
        return self

    def save(self):
        sn = self.xml.xpath(f'/properties/entry[@key="service.number"]')
        sn[0].text = f'{self._count}'
        super().save()
