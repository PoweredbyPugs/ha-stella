"""Asynchronous client for the Stella HTTP API."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

from aiohttp import ClientError, ClientSession


class StellaApiError(Exception):
    """Base exception for Stella API failures."""


class StellaAuthenticationError(StellaApiError):
    """Raised when Stella rejects the configured credentials."""


class StellaApiClient:
    """Small async client for endpoints used by Home Assistant."""

    def __init__(
        self, session: ClientSession, base_url: str, token: str | None
    ) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._headers = {"Accept": "application/json"}
        if token:
            self._headers["Authorization"] = f"Bearer {token}"

    async def async_health(self) -> dict[str, Any]:
        """Return health information from Stella."""
        return await self._request("get", "/health")

    async def async_snapshot(self) -> dict[str, Any]:
        """Return the current Stella snapshot."""
        payload = await self._request("get", "/v1/snapshot")
        data = payload.get("data")
        if not isinstance(data, dict):
            return payload
        return {
            "api_status": "partial" if payload.get("partial") else "online",
            **data,
            "snapshot_errors": payload.get("errors", {}),
            "partial": bool(payload.get("partial")),
        }

    async def async_call_tool(
        self, tool_name: str, arguments: Mapping[str, Any]
    ) -> dict[str, Any]:
        """Call a Stella read-only tool and return its response."""
        path = f"/v1/tools/{quote(tool_name, safe='')}"
        return await self._request("post", path, json=dict(arguments))

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Perform an API request and normalize failures."""
        request = getattr(self._session, method)
        try:
            async with request(
                f"{self._base_url}{path}", headers=self._headers, **kwargs
            ) as response:
                if response.status in (401, 403):
                    raise StellaAuthenticationError("Authentication rejected by Stella")
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except StellaAuthenticationError:
            raise
        except (ClientError, TimeoutError, OSError) as err:
            raise StellaApiError(f"Unable to communicate with Stella: {err}") from err
        except Exception as err:
            # Some aiohttp-compatible sessions use their own HTTP exception type.
            raise StellaApiError(f"Invalid response from Stella: {err}") from err

        if not isinstance(payload, dict):
            raise StellaApiError("Stella returned a non-object JSON response")
        return payload
