"""Constants for the Folding@Home integration."""

DOMAIN = 'foldingathome'

DEFAULT_PORT = 36330

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity

from homeassistant.const import (
    ATTR_ENTITY_ID,
)
ATTR_CONFIG = 'config'

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
)
CONF_CLIENTS = 'clients'
CONF_SLOT_ID = 'slot_id'

SERVICE_SET_IDLE = 'set_idle'
SERVICE_SET_POWER = 'set_power'
