import fah_api
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant

from . import const

_LOGGER = logging.getLogger(__name__)

CONFIG_CLIENT_SCHEMA = vol.Schema({
    vol.Required(const.CONF_HOST): str,
    vol.Optional(const.CONF_PORT, default=const.DEFAULT_PORT): vol.Coerce(int),
    vol.Optional(const.CONF_PASSWORD): str,
})


async def validate_input(hass: HomeAssistant, data: dict):
    _LOGGER.info("validate_input()")
    _LOGGER.info(data)

    host = data[const.CONF_HOST]
    password = data.get(const.CONF_PASSWORD)
    port = data.get(const.CONF_PORT)

    api = fah_api.API(host=host, password=password)
    try:
        api.info()
    except fah_api.errors.AuthException:
        raise PasswordError("Bad password")


class FoldingConfigFlow(config_entries.ConfigFlow, domain=const.DOMAIN):
    """Handle a config flow for Folding@Home"""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input = None):
        # This is called when:
        #  1. someone adds the integration in the UI
        #  2. someone deletes the integration in the UI
        _LOGGER.info("async_step_user()")

        errors = {}
        if user_input is not None:
            _LOGGER.info(user_input)

            api = fah_api.API(host=user_input['host'], port=user_input.get('port'), password=user_input.get('password'))
            try:
                api.info()
                return self.async_create_entry(title=user_input['host'], data=user_input)
            except fah_api.errors.AuthException:
                errors['base'] = 'password'
            except fah_api.errors.HostException:
                errors['base'] = 'hostname'
            except fah_api.errors.FahException:
                errors['base'] = 'connection'

        return self.async_show_form(
            step_id = "user", data_schema = CONFIG_CLIENT_SCHEMA, errors = errors
        )


class PasswordError(exceptions.HomeAssistantError):
    """Error to indicate the password was not accepted."""
