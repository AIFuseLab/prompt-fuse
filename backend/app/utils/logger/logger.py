import logging

class Logger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)

logger = Logger(__name__)