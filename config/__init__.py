"""
Configuration Module
Centralized settings management using Pydantic.
"""

from config.settings import Settings, get_settings

__all__ = [
    "Settings",
    "get_settings",
]
