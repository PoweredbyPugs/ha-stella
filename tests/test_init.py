"""Tests for setup and call_tool action."""

from unittest.mock import AsyncMock, patch

from homeassistant.const import CONF_TOKEN, CONF_URL
from homeassistant.core import SupportsResponse
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stella.const import DOMAIN


async def test_setup_and_service_response(hass) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_URL: "http://stella.local:3010", CONF_TOKEN: "token"},
    )
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.stella.StellaApiClient.async_snapshot",
            new=AsyncMock(return_value={"status": "ok"}),
        ),
        patch(
            "custom_components.stella.StellaApiClient.async_call_tool",
            new=AsyncMock(return_value={"result": "Waxing Crescent"}),
        ) as call_tool,
        patch.object(hass.config_entries, "async_forward_entry_setups", AsyncMock()),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        response = await hass.services.async_call(
            DOMAIN,
            "call_tool",
            {"tool_name": "moon_phase", "arguments": '{"date":"2026-09-04"}'},
            blocking=True,
            return_response=True,
        )

    assert response == {"result": "Waxing Crescent"}
    call_tool.assert_awaited_once_with("moon_phase", {"date": "2026-09-04"})
    assert hass.services.supports_response(DOMAIN, "call_tool") is SupportsResponse.ONLY


async def test_unsafe_tool_is_rejected(hass) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_URL: "http://stella.local:3010", CONF_TOKEN: ""}
    )
    entry.add_to_hass(hass)
    with (
        patch(
            "custom_components.stella.StellaApiClient.async_snapshot",
            new=AsyncMock(return_value={"status": "ok"}),
        ),
        patch.object(hass.config_entries, "async_forward_entry_setups", AsyncMock()),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        try:
            await hass.services.async_call(
                DOMAIN,
                "call_tool",
                {"tool_name": "raw_cypher", "arguments": {}},
                blocking=True,
                return_response=True,
            )
        except Exception as err:
            assert "not permitted" in str(err)
        else:
            raise AssertionError("Unsafe tool call should fail")
