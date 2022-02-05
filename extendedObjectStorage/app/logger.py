import logging.config
from app.config import CONFIG


logging.basicConfig()  # For logging into terminal
logger = logging.getLogger(CONFIG['serviceName'])
logger.setLevel(logging.DEBUG if CONFIG['logs']['enableDebug'] else logging.INFO)

logger.info(f"Logger has been configured")

