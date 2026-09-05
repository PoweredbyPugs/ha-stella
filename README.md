# Stella for Home Assistant

A HACS-compatible custom integration for a local [Stella](https://github.com/PoweredbyPugs/Stella-Astrological-System) API. It targets Home Assistant **2026.8 or newer**.

## Features

- UI config flow with a Stella base URL and optional bearer token
- Connection validation through `GET /health`
- Five-minute polling of `GET /v1/snapshot`
- Sensors for current moon sign, moon phase, current planetary-aspect count, planet count, and API status
- Connectivity binary sensor
- Response-capable `stella.call_tool` action using `POST /v1/tools/{name}`
- Privacy-preserving diagnostics (token redacted; snapshot/chart data omitted)

## Installation

### HACS custom repository

1. In HACS, add this repository as an **Integration** custom repository.
2. Install **Stella**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration**, search for **Stella**, and enter the API URL. The default is `http://punkR.local:3010`.

### Manual

Copy `custom_components/stella` into your Home Assistant `custom_components` directory, restart Home Assistant, and add Stella from the integrations UI.

## Action

`stella.call_tool` accepts `tool_name`, `arguments`, and an optional `config_entry_id` (only needed with multiple Stella instances). The action requires response data:

```yaml
action: stella.call_tool
data:
  tool_name: moon_phase
  arguments:
    date: "2026-09-04"
response_variable: stella_result
```

For defense in depth, the integration has a non-configurable denylist for raw Cypher, graph mutation/deletion, autopoietic, and memory tools. The upstream Stella API must still enforce authentication and authorization; this integration's filter is not a replacement for API-side security.

## Snapshot shape

The integration accepts common equivalent fields, including `moon.sign` / `current_moon_sign`, `moon.phase` / `moon_phase`, and list, mapping, or integer count forms for planets and aspects. Missing values display as unknown.

## Development

The full Home Assistant test suite requires Python 3.14.2+:

```bash
uv sync --extra test
uv run pytest
uv run ruff check .
```

No bearer tokens or personal chart data belong in issues, logs, fixtures, or diagnostics.
