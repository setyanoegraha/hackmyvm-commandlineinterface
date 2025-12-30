"""
Centralized access for all HMV-CLI modules.
This allows for cleaner imports in the main entry point and exposes package metadata.

Tool: HMV-CLI
Author: Ouba
GitHub: https://github.com/setyanoegraha/hackmyvm-commandlineinterface
"""

__tool_name__ = "HMV-CLI"
__version__ = "0.1.0"
__author__ = "Ouba"
__github_url__ = "https://github.com/setyanoegraha/hackmyvm-commandlineinterface"

from .auth import AuthManager
from .scraper import MachineScraper
from .download import DownloadManager
from .flag import FlagManager
from .writeups import WriteupManager

__all__ = [
    "AuthManager",
    "MachineScraper",
    "DownloadManager",
    "FlagManager",
    "WriteupManager",
    "__tool_name__",
    "__version__",
    "__author__",
    "__github_url__"
]