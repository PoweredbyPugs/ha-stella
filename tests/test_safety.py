"""Tests for Stella tool safety policy."""

import pytest

from custom_components.stella.safety import UnsafeToolError, ensure_tool_allowed


@pytest.mark.parametrize(
    "name",
    [
        "raw_cypher",
        "graph.delete_node",
        "delete-everything",
        "mutate_graph",
        "create_memory",
        "autopoietic_reflection",
        "neo4j_drop_database",
    ],
)
def test_unsafe_tools_are_denied(name: str) -> None:
    with pytest.raises(UnsafeToolError):
        ensure_tool_allowed(name)


@pytest.mark.parametrize(
    "name", ["current_transits", "moon_phase", "planetary_aspects"]
)
def test_read_only_tools_are_allowed(name: str) -> None:
    assert ensure_tool_allowed(name) == name


@pytest.mark.parametrize("name", ["", "   ", "../moon_phase", "moon/phase"])
def test_invalid_tool_names_are_denied(name: str) -> None:
    with pytest.raises(UnsafeToolError):
        ensure_tool_allowed(name)
