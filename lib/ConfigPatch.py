# Autor: Andrii Shapovalov
# Company: eGA
# Date: 2023-07-19
# Description: Parsing configuration file for the engine
from os import path
from lib.Singleton import singleton

@singleton
class ConfigPatch:
    """Клас для встановлення конфігурації"""
    NODE_VERSION = (None, '2.6', '2.7')
    COMPONENTS = (None, 'Connector', 'Service')

    def __init__(self, url: str = None, config_pach: str = None, node_version: str = None):
        self._url = url
        self._node_version = node_version
        self._config_pach = config_pach
        self._component = None
        self._remote_node_version = None

    def init(self, url: str = None, config_pach: str = None, component: str = None, node_version: str = None):
        self.url = url
        self.config_pach = config_pach
        self.component = component
        self.node_version = node_version

    @staticmethod
    def _chech_path(dir: str) -> str:
        """Перевіряє чи існує директорія"""
        if not path.exists(dir):
            raise ValueError(f'Path {dir} not found')
        return dir

    @property
    def config_pach(self) -> str | None:
        """Повертає шлях до конфігурації"""
        if not self._config_pach:
            return None
        if self.node_version == '2.6':
            return self._chech_path(self._config_pach)
        elif self.node_version == '2.7':
            if self.component == 'Connector':
                return self._chech_path(f'{self._config_pach}/connector')
            elif self.component == 'Service':
                return self._chech_path(f'{self._config_pach}/proxy')
            else:
                raise ValueError(f'Version must be {" or ".join(self.COMPONENTS)}')
        else:
            raise ValueError(f'Version must be {" or ".join(self.NODE_VERSION)}')

    @config_pach.setter
    def config_pach(self, value: str):
        """Встановлює шлях до конфігурації"""
        if not value:
            raise ValueError('Config path not set')
        self._config_pach = value

    @property
    def component(self) -> str:
        """Повертає компонент"""
        if not self._component:
            raise ValueError('Component not set')
        return self._component

    @component.setter
    def component(self, value: str):
        """Встановлює компонент"""
        if value not in self.COMPONENTS:
            raise ValueError(f'Version must be {" or ".join(self.COMPONENTS)}')
        self._component = value

    @property
    def node_version(self) -> str:
        """Повертає версію ноди"""
        if not self._node_version:
            raise ValueError('Version not set')
        return self._node_version

    @node_version.setter
    def node_version(self, value: str):
        """Встановлює версію ноди"""
        if value not in self.NODE_VERSION:
            raise ValueError(f'Version must be {" or ".join(self.NODE_VERSION)}')
        self._node_version = value

    @property
    def remote_node_version(self) -> str:
        """Повертає версію ноди країни-постачальника метаданих"""
        if not self._remote_node_version:
            if not self._node_version:
                raise ValueError('Version not set')
        return self._remote_node_version or self._node_version

    @remote_node_version.setter
    def remote_node_version(self, value: str):
        """Встановлює версію ноди країни-постачальника метаданих"""
        if value not in self.NODE_VERSION:
            raise ValueError(f'Version must be {" or ".join(self.NODE_VERSION)}')
        self._remote_node_version = value

    @property
    def url(self) -> str:
        """Повертає url країни-постачальника метаданих"""
        if self.remote_node_version == '2.6':
            if self.component == 'Connector':
                return f'{self._url}/EidasNode/ConnectorMetadata'
            elif self.component == 'Service':
                return f'{self._url}/EidasNode/ServiceMetadata'
            else:
                raise ValueError(f'Version must be {" or ".join(self.COMPONENTS)}')
        elif self.remote_node_version == '2.7':
            if self.component == 'Connector':
                return f'{self._url}/EidasNodeConnector/ConnectorMetadata'
            elif self.component == 'Service':
                return f'{self._url}/EidasNodeProxy/ServiceMetadata'
            else:
                raise ValueError(f'Version must be {" or ".join(self.COMPONENTS)}')
        else:
            raise ValueError(f'Version must be {" or ".join(self.NODE_VERSION)}')

    @url.setter
    def url(self, value: str):
        """Встановлює url країни-постачальника метаданих"""
        if not value:
            raise ValueError('Url not set')
        self._url = value
