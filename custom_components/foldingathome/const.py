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
ATTR_IDLE = 'run_on_idle'
ATTR_PAUSED = 'paused_by_user'
ATTR_PAUSED_REASON = 'paused_reason'
ATTR_PERCENT_DONE = 'percentdone'
ATTR_PROJECT = 'project'
ATTR_SLOT_ID = 'slot_id'
ATTR_WORKUNIT = 'workunit'

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
)
CONF_CLIENTS = 'clients'
CONF_HOSTS = 'host_entities'
CONF_SLOTS = 'slot_entities'

SERVICE_PAUSE = 'pause_slot'
SERVICE_SET_IDLE = 'set_slot_idle_flag'
SERVICE_SET_POWER = 'set_power'
SERVICE_UNPAUSE = 'unpause_slot'

SERVICE_PARAM_ENTITY_ID = 'entity_id'
SERVICE_PARAM_IDLE = 'idle'
SERVICE_PARAM_LEVEL = 'level'

POWER_LEVELS = [
    "LIGHT",
    "MEDIUM",
    "FULL"
]
