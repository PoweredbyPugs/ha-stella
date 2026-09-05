"""Constants for the Stella integration."""

from datetime import timedelta

DOMAIN = "stella"
DEFAULT_URL = "http://punkR.local:3010"
PLATFORMS = ["sensor", "binary_sensor"]
UPDATE_INTERVAL = timedelta(minutes=5)
SERVICE_CALL_TOOL = "call_tool"
ATTR_TOOL_NAME = "tool_name"
ATTR_ARGUMENTS = "arguments"
ATTR_CONFIG_ENTRY_ID = "config_entry_id"
