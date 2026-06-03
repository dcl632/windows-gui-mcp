"""Typed errors for the MCP layer."""

from __future__ import annotations


class GUIError(Exception):
    """Base class for all GUI automation errors."""


class WindowNotFound(GUIError):
    pass


class ElementNotFound(GUIError):
    pass


class VerifyFailed(GUIError):
    """Raised when an action's post-condition cannot be verified."""


class BackendUnavailable(GUIError):
    pass


class OCRUnavailable(GUIError):
    pass


class CoordinateClickRejected(GUIError):
    """Raised when caller asked for coordinate click without exhausting fallbacks."""
