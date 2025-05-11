import logging
import os
from datetime import datetime, timedelta
import multiprocessing


class LoggerManager:
    def __init__(self, name=__name__, level=logging.INFO, log_dir="test/data/log_data", cleanup_days=7):
        """
        Initializes the LoggerManager with the specified parameters.

        :param name: Name of the logger.
        :param level: Logging level (e.g., logging.INFO).
        :param log_dir: Directory to save log files. A new log file is created for each run.
        :param cleanup_days: Number of days to keep log files. Older files are deleted.
        """
        self.name = name
        self.level = level
        self.log_dir = log_dir
        self.cleanup_days = cleanup_days
        self.logger = self._setup_logger()

        if multiprocessing.current_process().name == "MainProcess":
            self._cleanup_logs()

    def _setup_logger(self):

        """
        Sets up the logger with console and file handlers, only in the main process.
        """
        logger = logging.getLogger(self.name)

        if multiprocessing.current_process().name != "MainProcess":
            return logger  
        
        if not logger.hasHandlers():  
            logger.setLevel(self.level)

            os.makedirs(self.log_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(self.log_dir, f"log_{timestamp}.log")

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(console_handler)

            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(file_handler)

            logger.info("Logger setup complete.")

        return logger

    def _cleanup_logs(self):

        """
        Deletes log files older than 7 days.
        """
        now = datetime.now()
        cutoff_time = now - timedelta(days=self.cleanup_days)

        for filename in os.listdir(self.log_dir):
            file_path = os.path.join(self.log_dir, filename)
            if os.path.isfile(file_path):
                file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if file_creation_time < cutoff_time:
                    try:
                        os.remove(file_path)
                        self.logger.info(f"Deleted old log file: {file_path}")
                    except Exception as e:
                        self.logger.error(f"Failed to delete {file_path}: {e}")

    def get_logger(self):
        """
        Returns the configured logger instance.
        """
        return self.logger


if multiprocessing.current_process().name == "MainProcess":
    logger_manager = LoggerManager(level=logging.INFO)
    logger = logger_manager.get_logger()
else:
    logger = logging.getLogger(__name__)
