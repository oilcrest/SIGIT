"""Service auto-discovery and registry.

The registry lazily scans ``sigit.services`` on first access and indexes
every :class:`BaseService` subclass it finds.  Contributors just drop a
new ``.py`` file into ``sigit/services/`` — no manual registration needed.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import Dict, List, Optional, Type

from .base import BaseService, Category


class ServiceRegistry:
    """Discovers and indexes every :class:`BaseService` in ``sigit/services/``."""

    _services: Dict[str, Type[BaseService]] = {}
    _ordered: List[Type[BaseService]] = []
    _discovered: bool = False

    @classmethod
    def discover(cls) -> None:
        """Walk ``sigit.services`` and register all ``BaseService`` subclasses."""
        if cls._discovered:
            return

        import sigit.services as pkg

        for _importer, modname, _ispkg in pkgutil.iter_modules(pkg.__path__):
            if modname.startswith("_"):
                continue
            module = importlib.import_module(f"sigit.services.{modname}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseService)
                    and attr is not BaseService
                    and hasattr(attr, "name")
                ):
                    cls._services[attr.name] = attr

        cls._ordered = sorted(cls._services.values(), key=lambda s: s.name)
        cls._discovered = True

    @classmethod
    def all(cls) -> Dict[str, Type[BaseService]]:
        """Return ``{name: ServiceClass}`` mapping."""
        cls.discover()
        return dict(cls._services)

    @classmethod
    def ordered(cls) -> List[Type[BaseService]]:
        """Return services sorted alphabetically by name."""
        cls.discover()
        return list(cls._ordered)

    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseService]]:
        """Lookup a single service by name (case-sensitive)."""
        cls.discover()
        return cls._services.get(name)

    @classmethod
    def by_category(cls, category: Category) -> List[Type[BaseService]]:
        """Filter services belonging to *category*."""
        cls.discover()
        return [s for s in cls._ordered if s.category == category]

    @classmethod
    def count(cls) -> int:
        """Total number of registered services."""
        cls.discover()
        return len(cls._services)
