"""Tests for diagnostics redaction."""

from homeassistant.const import CONF_TOKEN, CONF_URL
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stella.const import DOMAIN
from custom_components.stella.diagnostics import async_get_config_entry_diagnostics


async def test_token_is_redacted(hass) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_URL: "http://stella.local:3010", CONF_TOKEN: "top-secret"},
    )
    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["config_entry"][CONF_TOKEN] == "**REDACTED**"
    assert "top-secret" not in str(result)
