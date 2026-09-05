"""Stella integration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import CONF_TOKEN, CONF_URL
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import StellaApiClient, StellaApiError
from .const import (
    ATTR_ARGUMENTS,
    ATTR_CONFIG_ENTRY_ID,
    ATTR_TOOL_NAME,
    DOMAIN,
    PLATFORMS,
    SERVICE_CALL_TOOL,
)
from .coordinator import StellaDataUpdateCoordinator
from .safety import UnsafeToolError, ensure_tool_allowed


@dataclass
class StellaRuntimeData:
    """Runtime state associated with one Stella config entry."""

    client: StellaApiClient
    coordinator: StellaDataUpdateCoordinator


type StellaConfigEntry = ConfigEntry[StellaRuntimeData]

_CALL_TOOL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TOOL_NAME): cv.string,
        vol.Optional(ATTR_ARGUMENTS, default={}): vol.Any(dict, cv.string),
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
    }
)


def _parse_arguments(value: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError) as err:
        raise ServiceValidationError("arguments must be valid JSON") from err
    if not isinstance(parsed, dict):
        raise ServiceValidationError("arguments JSON must contain an object")
    return parsed


def _select_entry(hass: HomeAssistant, entry_id: str | None) -> StellaConfigEntry:
    loaded = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.state is ConfigEntryState.LOADED
    ]
    if entry_id:
        loaded = [entry for entry in loaded if entry.entry_id == entry_id]
    if not loaded:
        raise ServiceValidationError("No loaded Stella config entry was found")
    if len(loaded) > 1:
        raise ServiceValidationError(
            "Multiple Stella entries are loaded; provide config_entry_id"
        )
    return loaded[0]


async def _async_handle_call_tool(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    try:
        tool_name = ensure_tool_allowed(call.data[ATTR_TOOL_NAME])
    except UnsafeToolError as err:
        raise ServiceValidationError(str(err)) from err
    arguments = _parse_arguments(call.data[ATTR_ARGUMENTS])
    entry = _select_entry(hass, call.data.get(ATTR_CONFIG_ENTRY_ID))
    try:
        return await entry.runtime_data.client.async_call_tool(tool_name, arguments)
    except StellaApiError as err:
        raise HomeAssistantError(f"Stella tool call failed: {err}") from err


async def async_setup_entry(hass: HomeAssistant, entry: StellaConfigEntry) -> bool:
    """Set up Stella from a config entry."""
    client = StellaApiClient(
        async_get_clientsession(hass), entry.data[CONF_URL], entry.data.get(CONF_TOKEN)
    )
    coordinator = StellaDataUpdateCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = StellaRuntimeData(client, coordinator)

    if not hass.services.has_service(DOMAIN, SERVICE_CALL_TOOL):

        async def async_handle_call_tool(call: ServiceCall) -> dict[str, Any]:
            return await _async_handle_call_tool(hass, call)

        hass.services.async_register(
            DOMAIN,
            SERVICE_CALL_TOOL,
            async_handle_call_tool,
            schema=_CALL_TOOL_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: StellaConfigEntry) -> bool:
    """Unload a Stella config entry."""
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False

    other_loaded = any(
        candidate.entry_id != entry.entry_id
        and getattr(candidate, "runtime_data", None) is not None
        for candidate in hass.config_entries.async_entries(DOMAIN)
    )
    if not other_loaded:
        hass.services.async_remove(DOMAIN, SERVICE_CALL_TOOL)
    return True
