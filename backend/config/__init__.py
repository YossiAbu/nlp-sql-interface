# config/__init__.py
"""Configuration package for backend application."""
from .logging_config import setup_logging, logger

__all__ = ["setup_logging", "logger"]

