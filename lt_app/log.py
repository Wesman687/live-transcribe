import logging

logger = logging.getLogger("lt_app")
logger.setLevel(logging.DEBUG)

# Optional: Add console handler
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
