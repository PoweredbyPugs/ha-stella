"""Binary sensor platform for Stella."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import StellaDataUpdateCoordinator
from .entity import StellaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: StellaDataUpdateCoordinator = entry.runtime_data.coordinator
    async_add_entities([StellaConnectedBinarySensor(coordinator)])


class StellaConnectedBinarySensor(StellaEntity, BinarySensorEntity):
    """Report whether the most recent Stella update succeeded."""

    _attr_translation_key = "connected"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: StellaDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_connected"

    @property
    def is_on(self) -> bool:
        return self.coordinator.last_update_success
