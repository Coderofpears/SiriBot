"""Logging configuration for SiriBot."""
import logging
import sys
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console

console = Console()

def setup_logger(log_level: str = "INFO") -> logging.Logger:
    """Set up SiriBot logger with rich formatting."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )
    
    logger = logging.getLogger("siribot")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    return logger

logger = setup_logger()
