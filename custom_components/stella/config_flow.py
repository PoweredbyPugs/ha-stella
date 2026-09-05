"""Config flow for Stella."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit, urlunsplit

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_TOKEN, CONF_URL
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import StellaApiClient, StellaAuthenticationError
from .const import DEFAULT_URL, DOMAIN


def _normalize_url(value: str) -> str:
    value = value.strip().rstrip("/")
    parsed = urlsplit(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("A valid HTTP(S) URL is required")
    if parsed.query or parsed.fragment:
        raise ValueError("The base URL cannot contain a query or fragment")
    return urlunsplit((parsed.scheme.lower(), parsed.netloc, parsed.path, "", ""))


class StellaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Stella config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                url = _normalize_url(user_input[CONF_URL])
                token = user_input.get(CONF_TOKEN, "").strip()
                client = StellaApiClient(async_get_clientsession(self.hass), url, token)
                await client.async_health()
            except StellaAuthenticationError:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(url.casefold())
                self._abort_if_unique_id_configured()
                title = urlsplit(url).netloc
                return self.async_create_entry(
                    title=title, data={CONF_URL: url, CONF_TOKEN: token}
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_URL,
                    default=(user_input or {}).get(CONF_URL, DEFAULT_URL),
                ): str,
                vol.Optional(
                    CONF_TOKEN, default=(user_input or {}).get(CONF_TOKEN, "")
                ): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
