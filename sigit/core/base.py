"""Base service interface and result types for SIGIT.

This module defines the contracts that all SIGIT services must implement.
New services only need to subclass ``BaseService`` and implement ``execute()``.

Example::

    class MyTool(BaseService):
        name = "MyTool"
        description = "Does something useful"
        category = Category.NETWORK
        input_type = InputType.DOMAIN
        input_label = "enter domain"

        async def execute(self, target: str) -> ServiceResult:
            return ServiceResult.ok({"key": "value"})
"""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class InputType(enum.Enum):
    """Describes what type of input the service expects from the user."""

    USERNAME = "username"
    DOMAIN = "domain"
    IP = "ip"
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"
    NAME = "name"
    TARGET = "target"  # generic — domain or IP


class Category(enum.Enum):
    """Logical grouping for services (used by CLI menu and Web UI)."""

    SOCIAL = "Social"
    NETWORK = "Network"
    EMAIL = "Email"
    DOMAIN = "Domain"
    SECURITY = "Security"
    RECON = "Reconnaissance"


class ResultType(enum.Enum):
    """Controls how the result is rendered in CLI / Web UI."""

    KEY_VALUE = "key_value"   # Dict[str, Any]
    TABLE = "table"           # List[Dict[str, Any]]
    LIST = "list"             # List[str]
    TEXT = "text"             # str
    SCORED = "scored"         # Dict with 'score', 'total', 'percentage'


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ServiceResult:
    """Immutable, standardized result returned by every service."""

    success: bool
    data: Any
    error: Optional[str] = None
    result_type: ResultType = ResultType.KEY_VALUE
    save_filename: Optional[str] = None

    @classmethod
    def ok(
        cls,
        data: Any,
        *,
        result_type: ResultType = ResultType.KEY_VALUE,
        save_filename: Optional[str] = None,
    ) -> ServiceResult:
        """Shorthand for a successful result."""
        return cls(
            success=True, data=data,
            result_type=result_type, save_filename=save_filename,
        )

    @classmethod
    def fail(cls, error: str) -> ServiceResult:
        """Shorthand for a failed result."""
        return cls(success=False, data=None, error=error)


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class BaseService(ABC):
    """Abstract base for every SIGIT tool.

    Subclass this, set the five class-level metadata fields, and implement
    ``execute()``.  The :class:`ServiceRegistry` will pick it up
    automatically — no extra registration step required.
    """

    # ---- required class-level metadata (override in subclasses) ----
    name: ClassVar[str]
    description: ClassVar[str]
    category: ClassVar[Category]
    input_type: ClassVar[InputType]
    input_label: ClassVar[str]

    @abstractmethod
    async def execute(self, target: str) -> ServiceResult:
        """Run the tool against *target* and return a :class:`ServiceResult`."""
        ...
