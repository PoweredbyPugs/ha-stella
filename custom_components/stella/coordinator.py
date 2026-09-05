"""Data coordinator for Stella."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import StellaApiClient, StellaApiError
from .const import DOMAIN, UPDATE_INTERVAL


class StellaDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll Stella's current snapshot."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, client: StellaApiClient
    ) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            config_entry=entry,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.async_snapshot()
        except StellaApiError as err:
            raise UpdateFailed(str(err)) from err
