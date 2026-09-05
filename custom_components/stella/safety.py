"""Safety policy for Stella API tool calls."""

import re

# Stella exposes both observational tools and powerful graph/agent internals. Tool
# names matching these tokens are never forwarded, regardless of API permissions.
_DENIED_PATTERNS = (
    re.compile(r"(^|[._-])(?:raw[._-]?)?cypher($|[._-])", re.IGNORECASE),
    re.compile(r"(^|[._-])(?:delete|drop|detach|remove)($|[._-])", re.IGNORECASE),
    re.compile(
        r"(^|[._-])(?:graph[._-]?mutat|mutat(?:e|ion)?[._-]?graph)", re.IGNORECASE
    ),
    re.compile(
        r"(^|[._-])(?:create|merge|update|set)[._-]?(?:node|edge|relationship|property)",
        re.IGNORECASE,
    ),
    re.compile(r"(^|[._-])autopoiet", re.IGNORECASE),
    re.compile(r"(^|[._-])memory($|[._-])", re.IGNORECASE),
    re.compile(r"(^|[._-])(?:create|write|update|delete)[._-]?memor", re.IGNORECASE),
)
_VALID_TOOL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class UnsafeToolError(ValueError):
    """Raised when a tool name fails Stella's internal safety policy."""


def ensure_tool_allowed(tool_name: str) -> str:
    """Validate a tool name and enforce the non-configurable denylist."""
    name = tool_name.strip()
    if not _VALID_TOOL_NAME.fullmatch(name):
        raise UnsafeToolError("Tool name is invalid or not permitted")
    if any(pattern.search(name) for pattern in _DENIED_PATTERNS):
        raise UnsafeToolError(
            f"Tool '{name}' is not permitted by the Stella safety policy"
        )
    return name
