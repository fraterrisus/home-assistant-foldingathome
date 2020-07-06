import fah_api
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, callback

from . import const

_LOGGER = logging.getLogger(__name__)

class FahServices:
    def __init__(self, hass: HomeAssistant, api: fah_api.API):
        _LOGGER.info('__init__()')
        self._api = api
        self._hass = hass

    @callback
    def async_register(self):
        """Register our services."""
        _LOGGER.info('async_register()')
        self._hass.services.async_register(
            const.DOMAIN,
            const.SERVICE_SET_IDLE,
            self.async_handle_set_idle,
            schema=vol.Schema({
                vol.Optional(const.SERVICE_PARAM_IDLE, default=True): vol.Coerce(bool)
            })
        )

    async def async_handle_set_idle(self, service):
        idle = service.data[const.SERVICE_PARAM_IDLE]
        slot_id = 0
        self._api.set_idle(idle, slot_id)
