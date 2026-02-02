"""Pygame UI modals package.

This package provides modal dialogs for the pygame UI:
- BaseModal: Base class for all modals
- ConfirmModal: Yes/No confirmation dialog
- ErrorModal: Error message dialog with OK button
- WrestlerInspectModal: Detailed wrestler inspection dialog
"""

from .base import BaseModal
from .confirm import ConfirmModal
from .error import ErrorModal
from .inspect import WrestlerInspectModal

__all__ = ["BaseModal", "ConfirmModal", "ErrorModal", "WrestlerInspectModal"]
