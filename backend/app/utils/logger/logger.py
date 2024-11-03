import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, log_dir="logs", log_level=logging.INFO):
        """
        Initialize the Logger instance.
        
        Parameters:
            log_dir (str): Directory where the log file will be saved.
            log_level (int): The logging level. Default is logging.INFO.
        """
        self.log_dir = log_dir
        self.log_level = log_level
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.log_level)
        self._setup_logger()

    def _setup_logger(self):
        """Sets up the logger with a file and console handler."""
        # Ensure log directory exists
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Set log file name based on the current date
        log_filename = os.path.join(self.log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

        # Formatter for log messages
        log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # File handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(log_format)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(log_format)

        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, message):
        """Log an info message."""
        self.logger.info(message)

    def debug(self, message):
        """Log a debug message."""
        self.logger.debug(message)

    def warning(self, message):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message):
        """Log an error message."""
        self.logger.error(message)

    def critical(self, message):
        """Log a critical message."""
        self.logger.critical(message)

logger = Logger(log_dir="logs", log_level=logging.DEBUG)