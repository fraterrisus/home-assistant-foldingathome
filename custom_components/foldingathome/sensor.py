import asyncio
import hashlib
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA

from . import const
from .host import FahHost
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
    hostname = config[const.CONF_HOST]
    port = config[const.CONF_PORT]
    password = config[const.CONF_PASSWORD]

    host = FahHost(hostname=hostname, port=port, password=password)
    num_slots = host.num_slots()
    async_add_devices([host])
    hass.data[const.DOMAIN]['host_entities'].append(host)

    slots = []
    for slot_id in range(0, num_slots):
        _LOGGER.info("building slot %d" % slot_id)
        slot = FahSlot(slot_id=slot_id, host=host)
        slots.append(slot)

    if slots:
        hass.data[const.DOMAIN]['slot_entities'].extend(slots)
        async_add_devices(slots)

    _LOGGER.info(hass.data[const.DOMAIN])


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
        # TODO: remove entity from slot_entities and host_entities

    return unload_ok
