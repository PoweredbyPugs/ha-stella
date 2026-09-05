"""Tests for the Stella HTTP client."""

from unittest.mock import MagicMock

import pytest

from custom_components.stella.api import StellaApiClient, StellaApiError


class Response:
    def __init__(self, status: int, payload=None) -> None:
        self.status = status
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise RuntimeError(f"HTTP {self.status}")

    async def json(self, content_type=None):
        return self._payload


def session_with(method: str, response: Response):
    session = MagicMock()
    setattr(session, method, MagicMock(return_value=response))
    return session


@pytest.mark.asyncio
async def test_health_sends_bearer_token() -> None:
    session = session_with("get", Response(200, {"status": "ok"}))
    client = StellaApiClient(session, "http://example.test/", "secret")

    assert await client.async_health() == {"status": "ok"}
    session.get.assert_called_once_with(
        "http://example.test/health",
        headers={"Authorization": "Bearer secret", "Accept": "application/json"},
    )


@pytest.mark.asyncio
async def test_snapshot_endpoint() -> None:
    session = session_with("get", Response(200, {"moon": {"sign": "Leo"}}))
    client = StellaApiClient(session, "http://example.test", None)

    assert await client.async_snapshot() == {"moon": {"sign": "Leo"}}
    session.get.assert_called_once_with(
        "http://example.test/v1/snapshot", headers={"Accept": "application/json"}
    )


@pytest.mark.asyncio
async def test_snapshot_unwraps_bridge_envelope() -> None:
    session = session_with(
        "get",
        Response(
            200,
            {
                "data": {
                    "moon": {"moonSign": "Leo", "moonPhase": "Full Moon"},
                    "planets": {"planets": [{"name": "Sun"}]},
                },
                "errors": {},
                "partial": False,
            },
        ),
    )
    client = StellaApiClient(session, "http://example.test", None)

    assert await client.async_snapshot() == {
        "api_status": "online",
        "moon": {"moonSign": "Leo", "moonPhase": "Full Moon"},
        "planets": {"planets": [{"name": "Sun"}]},
        "snapshot_errors": {},
        "partial": False,
    }


@pytest.mark.asyncio
async def test_call_tool_posts_arguments() -> None:
    session = session_with("post", Response(200, {"result": 42}))
    client = StellaApiClient(session, "http://example.test", None)

    assert await client.async_call_tool("moon_phase", {"date": "2026-09-04"}) == {
        "result": 42
    }
    session.post.assert_called_once_with(
        "http://example.test/v1/tools/moon_phase",
        headers={"Accept": "application/json"},
        json={"date": "2026-09-04"},
    )


@pytest.mark.asyncio
async def test_non_object_response_is_rejected() -> None:
    session = session_with("get", Response(200, ["unexpected"]))
    client = StellaApiClient(session, "http://example.test", None)

    with pytest.raises(StellaApiError):
        await client.async_snapshot()
