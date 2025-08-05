import logging
from logging import Logger

def configure_logging() -> Logger:
    """Configure global logging and disable noisy loggers."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    return logging.getLogger(__name__)

# Create a global logger instance
logger: Logger = configure_logging()
