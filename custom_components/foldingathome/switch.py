import asyncio
import fah_api
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
        slots.append(FahSlot(host, slot_id, password))

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
    def __init__(self, host:str, slot_id:int, password:str = None):
        self._API = fah_api.API(host=host, password=password)
        self._description = None
        self._is_idle = None
        self._is_paused = None
        self._queue_info = {}
        self._slot_id = slot_id

    @property
    def is_on(self) -> bool:
        return not self._is_paused

    @property
    def percentdone(self) -> float:
        if 'percentdone' in self._queue_info:
            return float(str.replace(self._queue_info, '%', ''))
        else:
            return None

    @property
    def should_poll(self) -> bool:
        return True

    @property
    def slot_id(self) -> int:
        return self._slot_id

    async def async_turn_on(self, **kwargs) -> None:
        """Unpause the slot."""
        self._API.unpause(self._slot_id)

    async def async_turn_off(self, **kwargs) -> None:
        """Pause the slot."""
        self._API.pause(self._slot_id)

    async def async_update(self) -> None:
        """Read slot info and update state."""
        _LOGGER.info('async_update(%s,%d,%d)' % self._host, self._port, self._slot_id)

        slots_info = self._API.slot_info()
        slot_info = [s for s in slots_info if int(s['id']) == self._slot_id]
        if len(slot_info) != 1:
            raise Exception
        slot_info = slot_info[0]

        self._is_paused = bool(slot_info['options']['paused'])
        self._is_idle = bool(slot_info['idle'])
        self._description = slot_info['description']

        queues_info = self._API.queue_info()
        queue_info = [q for q in queues_info if int(q['slot']) == self._slot_id]
        if len(queue_info) == 0:
            self._queue_info = {}
        else:
            self._queue_info = queue_info[0]
