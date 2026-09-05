"""Tests for Stella config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_TOKEN, CONF_URL
from homeassistant.data_entry_flow import FlowResultType

from custom_components.stella.const import DOMAIN


async def test_user_flow(hass) -> None:
    with (
        patch(
            "custom_components.stella.config_flow.StellaApiClient.async_health",
            new=AsyncMock(return_value={"status": "ok"}),
        ),
        patch(
            "custom_components.stella.StellaApiClient.async_snapshot",
            new=AsyncMock(return_value={"status": "ok"}),
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={CONF_URL: "http://stella.local:3010/", CONF_TOKEN: "token"},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Stella"
    assert result["data"] == {
        CONF_URL: "http://stella.local:3010",
        CONF_TOKEN: "token",
    }


async def test_cannot_connect(hass) -> None:
    with patch(
        "custom_components.stella.config_flow.StellaApiClient.async_health",
        new=AsyncMock(side_effect=Exception("offline")),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={CONF_URL: "http://stella.local:3010", CONF_TOKEN: ""},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
