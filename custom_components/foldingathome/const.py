"""Constants for the Folding@Home integration."""

DOMAIN = 'foldingathome'

DEFAULT_PORT = 36330

from homeassistant.const import (
    ATTR_ENTITY_ID,
)
ATTR_ASSIGNED_DATE = 'assigned'
ATTR_CONFIG = 'config'
ATTR_CREDIT = 'basecredit'
ATTR_DESCRIPTION = 'description'
ATTR_DEADLINE = 'deadline'
ATTR_ESTIMATED_CREDIT = 'creditestimate'
ATTR_ESTIMATED_COMPLETION = 'eta'
ATTR_PAUSED = 'paused'
ATTR_PERCENT_DONE = 'percentdone'
ATTR_PROJECT = 'project'
ATTR_SLOT_ID = 'slot_id'

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
)
CONF_CLIENTS = 'clients'

SERVICE_SET_IDLE = 'set_idle'
SERVICE_SET_POWER = 'set_power'
SERVICE_PARAM_IDLE = 'idle'
SERVICE_PARAM_LEVEL = 'level'
