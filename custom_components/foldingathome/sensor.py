import asyncio
import fah_api
import hashlib
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA

from . import const
from .slot import FahSlot


_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(const.CONF_HOST): cv.string,
    vol.Optional(const.CONF_PASSWORD): cv.string,
    vol.Optional(const.CONF_PORT): vol.Coerce(int)
})


async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry,
        async_add_entities, discovery_info=None):
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
        slot = FahSlot(host, port, slot_id, password)
        # await slot.async_update()
        slots.append(slot)

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
