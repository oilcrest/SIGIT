"""SIGIT Core — base classes, client, config, and registry."""

from .base import BaseService, ServiceResult, InputType, Category, ResultType
from .client import AsyncClient
from .config import config
from .colors import Colors
from .registry import ServiceRegistry

__all__ = [
    "BaseService", "ServiceResult", "InputType", "Category", "ResultType",
    "AsyncClient", "config", "Colors", "ServiceRegistry",
]
