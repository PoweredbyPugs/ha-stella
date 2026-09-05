"""Base entity for Stella."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import StellaDataUpdateCoordinator


class StellaEntity(CoordinatorEntity[StellaDataUpdateCoordinator]):
    """Base coordinator-backed Stella entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: StellaDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title or "Stella",
            manufacturer="Stella",
            model="Astrology API",
            configuration_url=entry.data.get("url"),
        )
