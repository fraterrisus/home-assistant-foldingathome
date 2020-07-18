import asyncio
import fah_api
import hashlib
import logging

from homeassistant.helpers.entity import Entity

from . import const

_LOGGER = logging.getLogger(__name__)

class FahHost(Entity):
    def __init__(self, *, hostname:str, port:int, password:str = None):
        self.api = fah_api.API(host=hostname, port=port, password=password)
        self.hostname = hostname
        self.port = port
        self._info = {}
        self._options = {}
        self._state = 'on'

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {
                (const.DOMAIN, self.hostname, self.port)
            },
            "name": "%s:%d" % (self.hostname, self.port),
            "entry_type": 'service',
            "manufacturer": 'Folding@Home'
        }

    @property
    def device_state_attributes(self) -> dict:
        return {
            'build_version': self.get_attr('Build', 'Version'),
            'num_cpus': self.get_attr('System', 'CPUs'),
            'num_gpus': self.get_attr('System', 'GPUs'),
            'system_arch': self.get_attr('System', 'OS Arch'),
            'system_os': self.get_attr('System', 'OS'),
            'system_thread_model': self.get_attr('System', 'Threads')
        }

    @property
    def friendly_name(self) -> str:
        return "%s" % (self.hostname)

    @property
    def is_on(self) -> bool:
        return self.power() != 'off'

    @property
    def name(self) -> str:
        return "folding-%s" % (self.hostname)

    @property
    def should_poll(self) -> bool:
        return True

    @property
    def state(self) -> str:
        return self.power()

    @property
    def unique_id(self) -> str:
        id = 'foldingathome:%s:%d' % (self.hostname, self.port)
        return hashlib.md5(id.encode()).hexdigest()

    # Helpers

    def client_info(self) -> dict:
        data = self.api.info()
        return { data[i][0] : self.transpose_dict(data[i][1:])
            for i in range(0, len(data)) }

    def get_attr(self, *keys):
        dct = self._info
        for key in keys:
            try:
                dct = dct[key]
            except KeyError:
                return None
        return dct

    def num_slots(self) -> int:
        return self.api.num_slots()

    def power(self) -> str:
        if self._options is None: return 'off'
        return self._options.get('power')

    def transpose_dict(self, data:list) -> dict:
        return dict(zip([s[0] for s in data], [s[1] for s in data]))

    # Services

    async def async_update(self) -> None:
        """Read host info and update in-memory state."""
        self._info = self.client_info()
        self._options = self.api.options()

    def service_set_power(self, level:str) -> None:
        _LOGGER.info("service_set_power(%d)" % level)
        self.api.set_power(level)
