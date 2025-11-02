import logging
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter

LOG_FORMAT_COLORED = (
    "\033[37m%(asctime)s "                          # White timestamp
    "%(log_color)s[%(levelname)s] "                 # Colored level name
    "\033[38;5;111m%(name)s:\033[0m "               # Light bluish-purple name
    "\033[37m%(message)s"
)

LOG_FORMAT_PLAIN = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_LEVEL = logging.DEBUG

def setup_logging(log_file: str = "app.log"):
    color_formatter = ColoredFormatter(
        LOG_FORMAT_COLORED,
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red',
        },
    )
    plain_formatter = logging.Formatter(LOG_FORMAT_PLAIN)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)
    console_handler.setLevel(LOG_LEVEL)

    file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3)
    file_handler.setFormatter(plain_formatter)
    file_handler.setLevel(LOG_LEVEL)

    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    root_logger.handlers = []
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    logger = logging.getLogger("uvicorn")
    logger.handlers = []
    logger.propagate = True
    logger.setLevel(LOG_LEVEL)
