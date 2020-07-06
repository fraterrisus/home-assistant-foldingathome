import asyncio
import fah_api
import hashlib
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA

from . import const

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(const.CONF_HOST): cv.string,
    vol.Optional(const.CONF_PASSWORD): cv.string,
    vol.Optional(const.CONF_PORT): vol.Coerce(int)
})

class FahSlot(Entity):
    def __init__(self, host:str, port:int, slot_id:int, password:str = None):
        self._API = fah_api.API(host=host, password=password)
        self._host = host
        self._port = port
        self._queue_info = {}
        self._slot_info = {}
        self._slot_id = slot_id

    # Properties

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {
                (const.DOMAIN, self._host, self._port)
            },
            "name": "%s:%d" % (self._host, self._port),
            "entry_type": 'service',
            "manufacturer": 'Folding@Home'
        }

    @property
    def device_state_attributes(self) -> dict:
        return {
            const.CONF_HOST: self._host,
            const.CONF_PORT: self._port,
            const.ATTR_ASSIGNED_DATE: self._queue_info.get(const.ATTR_ASSIGNED_DATE),
            const.ATTR_CREDIT: self._queue_info.get(const.ATTR_CREDIT),
            const.ATTR_DEADLINE: self._queue_info.get(const.ATTR_DEADLINE),
            const.ATTR_DESCRIPTION: self._slot_info.get(const.ATTR_DESCRIPTION),
            const.ATTR_ESTIMATED_COMPLETION: self._queue_info.get(const.ATTR_ESTIMATED_COMPLETION),
            const.ATTR_PERCENT_DONE: self.percentdone(),
            const.ATTR_PROJECT: self._queue_info.get(const.ATTR_PROJECT),
            const.ATTR_SLOT_ID: self._slot_id
        }

    @property
    def friendly_name(self) -> str:
        return "%s slot %d" % (self._host, self._slot_id)

    @property
    def is_on(self) -> bool:
        return not self.paused()

    @property
    def name(self) -> str:
        return "folding-%s-slot-%d" % (self._host, self._slot_id)

    @property
    def should_poll(self) -> bool:
        return True

    @property
    def state(self) -> str:
        return self.status()

    @property
    def unique_id(self) -> str:
        id = 'foldingathome:%s:%d:%d' % (self._host, self._port, self._slot_id)
        return hashlib.md5(id.encode()).hexdigest()

    # Attribute helpers

    def client_info(self) -> dict:
        data = self._API.info()
        return { data[i][0] : self.transpose_dict(data[i][1:])
            for i in range(0, len(data)) }

    def paused(self) -> bool:
        slot_options = self._slot_info.get('options')
        if slot_options is None:
            return True
        return slot_options.get(const.ATTR_PAUSED) == 'true'

    def percentdone(self) -> float:
        percentdone = self._queue_info.get(const.ATTR_PERCENT_DONE)
        if percentdone is not None:
            percentdone = float(str.replace(percentdone, '%', ''))
        return percentdone

    def status(self) -> str:
        status = self._slot_info.get('status')
        if status is None:
            status = 'NOTFOUND'
        return status

    def transpose_dict(self, data:list) -> dict:
        return dict(zip([s[0] for s in data], [s[1] for s in data]))

    # Services

    async def async_update(self) -> None:
        """Read slot info and update in-memory state."""
        slots_info = self._API.slot_info()
        slot_info = [s for s in slots_info if int(s['id']) == self._slot_id]
        if len(slot_info) == 0:
            self._slot_info = {}
        else:
            self._slot_info = slot_info[0]

        queues_info = self._API.queue_info()
        queue_info = [q for q in queues_info if int(q['slot']) == self._slot_id]
        if len(queue_info) == 0:
            self._queue_info = {}
        else:
            self._queue_info = queue_info[0]
