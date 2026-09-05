"""Tests for Stella snapshot value extraction."""

from custom_components.stella.sensor import (
    _aspects_count,
    _moon_phase,
    _moon_sign,
    _planets_count,
)


def test_extracts_live_helios_snapshot_shape() -> None:
    data = {
        "moon": {"moonSign": "Taurus", "moonPhase": "Last Quarter"},
        "planets": {"localEasternTime": "ignored", "planets": [{}, {}]},
        "aspects": {"localEasternTime": "ignored", "aspects": [{}, {}, {}]},
    }

    assert _moon_sign(data) == "Taurus"
    assert _moon_phase(data) == "Last Quarter"
    assert _planets_count(data) == 2
    assert _aspects_count(data) == 3