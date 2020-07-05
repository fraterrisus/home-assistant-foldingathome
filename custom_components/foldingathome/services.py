import fah_api
import voluptuous as vol

from homeassistant.core import HomeAssistant, callback

from . import const

class FahServices:
    def __init__(self, hass: HomeAssistant):
        self._hass = _hass

    @callback
    def async_register():
        """Register our services."""
        self._hass.services.async_register(
            const.DOMAIN,
            const.SERVICE_SET_IDLE,
            self.async_handle_set_idle,
            schema=vol.Schema({
                vol.Optional(const.ATTR_IDLE, default=True): vol.Coerce(bool)
            })
        )

    async def async_handle_set_idle(self, service):
        idle = service.data[const.ATTR_IDLE]
        slot_id = 0
        fah_api.set_idle(idle, slot_id)
