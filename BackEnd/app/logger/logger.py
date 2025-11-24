import structlog
from .logging_config import setup_logging

#Logging script
setup_logging()
log = structlog.get_logger()