import os
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


class Logger:
    def __init__(self, log_dir="logs", log_level=logging.INFO):
        self.logger = logging.getLogger('FastAPI_Logger')
        self.logger.setLevel(log_level)

        # Ensure log directory exists
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Info log handler
        info_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_dir, f"info.{datetime.now().year}{datetime.now().month}.log"),
            when='midnight',
            interval=1,
            backupCount=30
        )
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Error log handler
        error_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_dir, f"error.{datetime.now().year}{datetime.now().month}.log"),
            when='midnight',
            interval=1,
            backupCount=30
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Add handlers to logger
        self.logger.addHandler(info_handler)
        self.logger.addHandler(error_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def log_request(self, client_host, client_ip, user_agent, host, method, url):
        self.info(f"Request: {method} {url}, Client Host: {client_host}, Client IP: {client_ip}, User-Agent: {user_agent}, Host: {host}")

    def log_response(self, client_host, client_ip, user_agent, host, method, url, status_code):
        self.info(
            f"Response: {status_code} {method} {url}, Client Host: {client_host}, Client IP: {client_ip}, User-Agent: {user_agent}, Host: {host}")

    def log_exception(self, client_host, client_ip, user_agent, host, exception):
        self.error(f"Exception: {str(exception)}, Client Host: {client_host}, Client IP: {client_ip}, User-Agent: {user_agent}, Host: {host}")