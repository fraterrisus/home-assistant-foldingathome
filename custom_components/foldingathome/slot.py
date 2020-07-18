import asyncio
import hashlib
import logging

from homeassistant.helpers.entity import Entity

from . import (const, host)

_LOGGER = logging.getLogger(__name__)

class FahSlot(Entity):
    def __init__(self, *, slot_id:int, host:host.FahHost):
        self.host = host
        self._queue_info = {}
        self._slot_info = {}
        self._slot_id = slot_id

    # Properties

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {
                (const.DOMAIN, self.host.hostname, self.host.port)
            },
            "name": "%s:%d" % (self.host.hostname, self.host.port),
            "entry_type": 'service',
            "manufacturer": 'Folding@Home'
        }

    @property
    def device_state_attributes(self) -> dict:
        return {
            const.CONF_HOST: self.host.hostname,
            const.CONF_PORT: self.host.port,
            const.ATTR_SLOT_ID: self._slot_id,
            const.ATTR_DESCRIPTION: self._slot_info.get(const.ATTR_DESCRIPTION),
            const.ATTR_IDLE: self.get_attr(self._slot_info, 'options', 'idle') in ['True', 'true'],
            const.ATTR_PAUSED: self.get_attr(self._slot_info, 'options', 'paused') in ['True', 'true'],
            const.ATTR_PAUSED_REASON: self._slot_info.get('reason'),
            const.ATTR_WORKUNIT: self._queue_info.get('unit'),
            const.ATTR_PROJECT: self._queue_info.get(const.ATTR_PROJECT),
            const.ATTR_CREDIT: self._queue_info.get(const.ATTR_CREDIT),
            const.ATTR_PERCENT_DONE: self.percentdone(),
            const.ATTR_ESTIMATED_COMPLETION: self._queue_info.get(const.ATTR_ESTIMATED_COMPLETION),
            const.ATTR_ASSIGNED_DATE: self._queue_info.get(const.ATTR_ASSIGNED_DATE),
            const.ATTR_DEADLINE: self._queue_info.get(const.ATTR_DEADLINE),
        }

    @property
    def friendly_name(self) -> str:
        return "%s slot %d" % (self.host.hostname, self._slot_id)

    @property
    def is_on(self) -> bool:
        return not self.paused()

    @property
    def name(self) -> str:
        return "folding-%s-slot-%d" % (self.host.hostname, self._slot_id)

    @property
    def should_poll(self) -> bool:
        return True

    @property
    def state(self) -> str:
        return self.status()

    @property
    def unique_id(self) -> str:
        id = 'foldingathome:%s:%d:%d' % (self.host.hostname, self.host.port, self._slot_id)
        return hashlib.md5(id.encode()).hexdigest()

    # Helpers

    def get_attr(self, dct, *keys):
        for key in keys:
            try:
                dct = dct[key]
            except KeyError:
                return None
        return dct

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

    # Services

    async def async_update(self) -> None:
        """Read slot info and update in-memory state."""
        slots_info = self.host.api.slot_info()
        slot_info = [s for s in slots_info if int(s['id']) == self._slot_id]
        if len(slot_info) == 0:
            self._slot_info = {}
        else:
            self._slot_info = slot_info[0]

        queues_info = self.host.api.queue_info()
        queue_info = [q for q in queues_info if int(q['slot']) == self._slot_id]
        if len(queue_info) == 0:
            self._queue_info = {}
        else:
            self._queue_info = queue_info[0]

    def service_set_idle(self, idle:bool) -> None:
        _LOGGER.info("service_set_idle(%s,%d)" % (str(idle), self._slot_id))
        self.host.api.set_idle(idle, self._slot_id)

    def service_pause(self) -> None:
        _LOGGER.info("service_pause(%d)" % self._slot_id)
        self.host.api.pause(self._slot_id)

    def service_unpause(self) -> None:
        _LOGGER.info("service_unpause(%d)" % self._slot_id)
        self.host.api.unpause(self._slot_id)
