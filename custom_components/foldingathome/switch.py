import asyncio
import fah_api
import hashlib
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from . import const

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(const.CONF_HOST): cv.string,
    vol.Optional(const.CONF_PASSWORD): cv.string,
    vol.Optional(const.CONF_PORT): vol.Coerce(int)
})

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigEntry,
    async_add_entities,
    discovery_info=None):
    """Set up Folding@Home slots from config."""
    _LOGGER.info('async_setup_platform()')

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_devices):
    _LOGGER.info('async_setup_entry()')
    _LOGGER.info(entry.as_dict())

    config = entry.data
    _LOGGER.info(config)
    host = config[const.CONF_HOST]
    port = config[const.CONF_PORT]
    password = config[const.CONF_PASSWORD]

    api = fah_api.API(host=host, password=password)
    num_slots = api.num_slots()
    slots = []
    for slot_id in range(0, num_slots):
        _LOGGER.info("building slot %d" % slot_id)
        slots.append(FahSlot(host, port, slot_id, password))

    if slots:
        async_add_devices(slots)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[const.DOMAIN].pop(entry.entry_id)

    return unload_ok


class FahSlot(SwitchEntity):
    def __init__(self, host:str, port:int, slot_id:int, password:str = None):
        self._API = fah_api.API(host=host, password=password)
        self._host = host
        self._port = port
        self._queue_info = {}
        self._slot_info = {}
        self._slot_id = slot_id

    # Properties

    @property
    def device_class(self) -> str:
        return 'switch'

    @property
    def device_state_attributes(self) -> dict:
        return {
            const.CONF_HOST: self._host,
            const.CONF_PORT: self._port,
            const.ATTR_DESCRIPTION: self._slot_info.get('description'),
            const.ATTR_PERCENT_DONE: self.percentdone(),
            const.ATTR_SLOT_ID: self._slot_id
        }

    @property
    def friendly_name(self) -> str:
        return "Folding@Home %s Slot %d" % (self._host, self._slot_id)

    @property
    def is_on(self) -> bool:
        return not self.paused()

    @property
    def name(self) -> str:
        """Name of the device"""
        return "folding-%s-slot-%d" % (self._host, self._slot_id)

    @property
    def should_poll(self) -> bool:
        return True

    @property
    def unique_id(self) -> str:
        id = 'foldingathome:%s:%d:%d' % (self._host, self._port, self._slot_id)
        return hashlib.md5(id.encode()).hexdigest()

    # Attributes

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

    # Services

    async def async_turn_on(self, **kwargs) -> None:
        """Unpause the slot."""
        self._API.unpause(self._slot_id)

    async def async_turn_off(self, **kwargs) -> None:
        """Pause the slot."""
        self._API.pause(self._slot_id)

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
