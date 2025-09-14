__version__ = "1.1.4"

# Re-export logging setup helper for convenience
from .logging import setup_logging  # noqa: E402,F401

__all__ = ["__version__", "setup_logging"]