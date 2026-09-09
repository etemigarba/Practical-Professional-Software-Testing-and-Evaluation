"""Identifier patterns.

Slide 16 asserts ``expect(res.body.id).toMatch(UUID_V4)`` without ever defining
``UUID_V4``.  Gap resolved here, with a pattern strict enough to reject a v1
UUID rather than merely matching the general shape.
"""

from __future__ import annotations

import re
import uuid
from typing import Final

__all__ = ["UUID_V4_PATTERN", "is_uuid_v4", "new_id"]

UUID_V4_PATTERN: Final = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
"""Matches a canonical RFC 4122 version-4 UUID and nothing else.

The ``4`` in the third group pins the version; the ``[89ab]`` in the fourth pins
the variant.  A v1 UUID fails both.
"""


def is_uuid_v4(candidate: str) -> bool:
    """Return ``True`` only for a canonical v4 UUID string."""
    return UUID_V4_PATTERN.match(candidate) is not None


def new_id() -> str:
    """Generate a fresh v4 identifier."""
    return str(uuid.uuid4())
