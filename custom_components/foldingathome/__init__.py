"""The Folding@Home integration."""
import asyncio
import fah_api
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from . import const
from .services import FahServices
from .slot import FahSlot

_LOGGER = logging.getLogger(__name__)

CONFIG_CLIENT_SCHEMA = vol.Schema({
    vol.Required(const.CONF_HOST): cv.string,
    vol.Optional(const.CONF_PASSWORD): cv.string,
    vol.Optional(const.CONF_PORT): vol.Coerce(int)
})

CONFIG_SCHEMA = vol.Schema({
    const.DOMAIN: {
        vol.Optional(const.CONF_CLIENTS, default=[]): vol.All(
            cv.ensure_list, [CONFIG_CLIENT_SCHEMA]
        ),
#        vol.Optional(const.CONF_DISCOVERY, default=False): cv.boolean
    }
}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Folding@Home component."""
    _LOGGER.info("async_setup()")
    _LOGGER.info(config)

    conf = config.get(const.DOMAIN)
    hass.data[const.DOMAIN] = {}
    hass.data[const.DOMAIN][const.ATTR_CONFIG] = conf or {}

    _LOGGER.info(conf)
    # conf = OrderedDict([('clients', [OrderedDict([('host', '192.168.1.11'), ('password', 'putzfuck')])])])

### So this looks for things in the configuration file and kicks off... some sort of config flow for it?
#    if conf is not None:
#        hass.async_create_task(
#            hass.config_entries.flow.async_init(
#                const.DOMAIN, context={"source": config_entries.SOURCE_IMPORT}
#            )
#        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry):
    """Set up Folding@Home from a config entry."""
    # This gets called (at least) after a form-submit when the integration is set up in the UI.
    _LOGGER.info("async_setup_entry()")
    _LOGGER.info(entry.as_dict())

    config_data = hass.data[const.DOMAIN].get(const.ATTR_CONFIG)

    api = fah_api.API()
    services = FahServices(hass, api)
    services.async_register()

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
#    if unload_ok:
#        hass.data[const.DOMAIN].pop(entry.entry_id)

    return unload_ok
