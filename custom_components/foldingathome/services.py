import fah_api
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, callback

from . import const

_LOGGER = logging.getLogger(__name__)

class FahServices:
    def __init__(self, hass: HomeAssistant):
        _LOGGER.info('__init__()')
        self._hass = hass

    @callback
    def register_services(self):
        """Register our services."""
        _LOGGER.info('async_register()')

        self._hass.services.async_register(
            const.DOMAIN,
            const.SERVICE_SET_IDLE,
            self.async_handle_set_idle,
            schema=vol.Schema({
                vol.Optional(const.SERVICE_PARAM_IDLE, default=True): vol.Coerce(bool),
                vol.Required(const.SERVICE_PARAM_ENTITY_ID): vol.Any(str, list),
            })
        )

        self._hass.services.async_register(
            const.DOMAIN,
            const.SERVICE_SET_POWER,
            self.async_handle_set_power,
            schema=vol.Schema({
                vol.Required(const.SERVICE_PARAM_LEVEL): vol.Any('LIGHT', 'MEDIUM', 'FULL'),
                vol.Required(const.SERVICE_PARAM_ENTITY_ID): vol.Any(str, list),
            })
        )

        self._hass.services.async_register(
            const.DOMAIN,
            const.SERVICE_PAUSE,
            self.async_handle_pause_slot,
            schema=vol.Schema({
                vol.Required(const.SERVICE_PARAM_ENTITY_ID): vol.Any(str, list),
            })
        )

        self._hass.services.async_register(
            const.DOMAIN,
            const.SERVICE_UNPAUSE,
            self.async_handle_unpause_slot,
            schema=vol.Schema({
                vol.Required(const.SERVICE_PARAM_ENTITY_ID): vol.Any(str, list),
            })
        )


    def lookup_hosts(self, target_ids):
        #_LOGGER.info(self._hass.data[const.DOMAIN][const.CONF_SLOTS])
        target_entities = [
            entity
            for entity in self._hass.data[const.DOMAIN][const.CONF_HOSTS]
            if entity.entity_id in target_ids
        ]
        #_LOGGER.info(target_entities)
        return target_entities

    def lookup_slots(self, target_ids):
        #_LOGGER.info(self._hass.data[const.DOMAIN][const.CONF_SLOTS])
        target_entities = [
            entity
            for entity in self._hass.data[const.DOMAIN][const.CONF_SLOTS]
            if entity.entity_id in target_ids
        ]
        #_LOGGER.info(target_entities)
        return target_entities


    async def async_handle_set_idle(self, call):
        target_ids = call.data[const.SERVICE_PARAM_ENTITY_ID]
        idle = call.data[const.SERVICE_PARAM_IDLE]
        for target in self.lookup_slots(target_id):
            target.service_set_idle(idle)


    async def async_handle_set_power(self, call):
        target_id = call.data[const.SERVICE_PARAM_ENTITY_ID]
        level = call.data[const.SERVICE_PARAM_LEVEL]
        for target in self.lookup_hosts(target_id):
            target.service_set_power(level)


    async def async_handle_pause_slot(self, call):
        target_id = call.data[const.SERVICE_PARAM_ENTITY_ID]
        for target in self.lookup_slots(target_id):
            target.service_pause()


    async def async_handle_unpause_slot(self, call):
        target_id = call.data[const.SERVICE_PARAM_ENTITY_ID]
        for target in self.lookup_slots(target_id):
            target.service_unpause()
