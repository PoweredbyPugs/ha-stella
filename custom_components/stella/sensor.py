"""Sensor platform for Stella."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import StellaDataUpdateCoordinator
from .entity import StellaEntity


def _path(data: Mapping[str, Any], *paths: tuple[str, ...]) -> Any:
    for candidate in paths:
        value: Any = data
        for key in candidate:
            if not isinstance(value, Mapping) or key not in value:
                break
            value = value[key]
        else:
            return value
    return None


def _count(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, (list, tuple, set, Mapping)):
        return len(value)
    return None


def _moon_sign(data: Mapping[str, Any]) -> Any:
    return _path(
        data,
        ("current_moon_sign",),
        ("moon", "moonSign"),
        ("moon", "sign"),
        ("moon", "current_sign"),
    )


def _moon_phase(data: Mapping[str, Any]) -> Any:
    return _path(
        data,
        ("moon_phase",),
        ("moon", "moonPhase"),
        ("moon", "phase"),
        ("moon", "current_phase"),
    )


def _aspects_count(data: Mapping[str, Any]) -> int | None:
    return _count(
        _path(
            data,
            ("current_planetary_aspects",),
            ("aspects", "aspects"),
            ("aspects",),
            ("current_aspects",),
        )
    )


def _planets_count(data: Mapping[str, Any]) -> int | None:
    return _count(
        _path(data, ("planets", "planets"), ("planets",), ("current_planets",))
    )


def _api_status(data: Mapping[str, Any]) -> str:
    value = _path(data, ("api_status",), ("status",), ("health", "status"))
    return str(value) if value is not None else "online"


@dataclass(frozen=True, kw_only=True)
class StellaSensorEntityDescription(SensorEntityDescription):
    """Describe a Stella sensor."""

    value_fn: Callable[[Mapping[str, Any]], Any]


SENSORS = (
    StellaSensorEntityDescription(
        key="current_moon_sign",
        translation_key="current_moon_sign",
        value_fn=_moon_sign,
    ),
    StellaSensorEntityDescription(
        key="moon_phase", translation_key="moon_phase", value_fn=_moon_phase
    ),
    StellaSensorEntityDescription(
        key="current_planetary_aspects_count",
        translation_key="current_planetary_aspects_count",
        native_unit_of_measurement="aspects",
        value_fn=_aspects_count,
    ),
    StellaSensorEntityDescription(
        key="planets_count",
        translation_key="planets_count",
        native_unit_of_measurement="planets",
        value_fn=_planets_count,
    ),
    StellaSensorEntityDescription(
        key="api_status", translation_key="api_status", value_fn=_api_status
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: StellaDataUpdateCoordinator = entry.runtime_data.coordinator
    async_add_entities(
        StellaSensor(coordinator, description) for description in SENSORS
    )


class StellaSensor(StellaEntity, SensorEntity):
    """A sensor sourced from the Stella snapshot."""

    entity_description: StellaSensorEntityDescription

    def __init__(self, coordinator, description: StellaSensorEntityDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data or {})
