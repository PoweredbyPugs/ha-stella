"""Diagnostics support for Stella."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant

from . import StellaConfigEntry

_TO_REDACT = {CONF_TOKEN}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: StellaConfigEntry
) -> dict[str, Any]:
    """Return privacy-preserving diagnostics for a Stella entry."""
    diagnostics: dict[str, Any] = {
        "config_entry": async_redact_data(dict(entry.data), _TO_REDACT),
        "state": entry.state.value,
    }
    runtime_data = getattr(entry, "runtime_data", None)
    if runtime_data is not None:
        coordinator = runtime_data.coordinator
        diagnostics["coordinator"] = {
            "last_update_success": coordinator.last_update_success,
            "last_exception": (
                str(coordinator.last_exception)
                if coordinator.last_exception is not None
                else None
            ),
            "update_interval_seconds": int(coordinator.update_interval.total_seconds()),
        }
    # Deliberately omit snapshot data because it may contain personal chart data.
    return diagnostics
