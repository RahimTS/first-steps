from __future__ import annotations

from enum import Enum


class Collections(str, Enum):
    """Central registry of MongoDB collection names.

    Use these enum values instead of hardcoded strings across the codebase
    to keep collection names organised and consistent.
    """

    USERS = "users"
    COUNTERS = "counters"
