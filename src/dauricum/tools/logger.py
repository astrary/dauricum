import logging

class Formatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    light_red = "\033[91m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "\033[34m[%(asctime)s]\033[0m \033[32m[%(name)s/%(levelname)s]\033[0m: %(message)s"

    FORMATS = {
        logging.DEBUG: format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)

class Logger:
    logger = logging.getLogger(__name__)
    
    def init(enabled: bool, debug: bool):
        Logger.logger.setLevel(logging.DEBUG if debug else logging.INFO)

        py_handler = logging.StreamHandler()

        py_handler.setFormatter(Formatter())
        Logger.logger.addHandler(py_handler)
        Logger.logger.disabled = not enabled