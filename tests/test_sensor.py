"""Tests for Stella snapshot extraction."""

from custom_components.stella.sensor import (
    _api_status,
    _aspects_count,
    _moon_phase,
    _moon_sign,
    _planets_count,
)


def test_nested_snapshot_values() -> None:
    snapshot = {
        "moon": {"sign": "Leo", "phase": "Waxing Crescent"},
        "aspects": [{"type": "trine"}, {"type": "square"}],
        "planets": {"sun": {}, "moon": {}, "mercury": {}},
        "status": "ok",
    }

    assert _moon_sign(snapshot) == "Leo"
    assert _moon_phase(snapshot) == "Waxing Crescent"
    assert _aspects_count(snapshot) == 2
    assert _planets_count(snapshot) == 3
    assert _api_status(snapshot) == "ok"


def test_integer_counts_and_default_status() -> None:
    snapshot = {
        "current_moon_sign": "Virgo",
        "moon_phase": "First Quarter",
        "current_planetary_aspects": 4,
        "current_planets": 10,
    }

    assert _aspects_count(snapshot) == 4
    assert _planets_count(snapshot) == 10
    assert _api_status(snapshot) == "online"
