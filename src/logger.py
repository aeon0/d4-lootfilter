import inspect
import io
import logging
import os
import sys
import warnings

import colorama
from version import __version__

colorama.init()


class CustomFormatter(logging.Formatter):
    _format = f"[{__version__} %(asctime)s] %(levelname)-10s %(message)s"

    FORMATS = {
        logging.DEBUG: colorama.Fore.WHITE + _format + colorama.Fore.WHITE,
        logging.INFO: colorama.Fore.LIGHTBLUE_EX + _format + colorama.Fore.WHITE,
        logging.WARNING: colorama.Fore.LIGHTYELLOW_EX + _format + colorama.Fore.WHITE,
        logging.ERROR: colorama.Fore.LIGHTRED_EX + _format + colorama.Fore.WHITE,
        logging.CRITICAL: colorama.Fore.RED + _format + colorama.Fore.WHITE,
    }

    def _get_caller_info(self, stack_level):
        """Returns the module and function name of the caller at a given stack level."""
        stack = inspect.stack()
        frame_info = inspect.getframeinfo(stack[stack_level][0])
        function_name = frame_info.function
        module_name = inspect.getmodule(stack[stack_level][0]).__name__

        return module_name, function_name

    def format(self, record):
        stack_level = 10  # found manually to get correct level of module.function
        log_fmt = self.FORMATS.get(record.levelno)
        msg = record.getMessage()

        if record.levelno in (logging.WARNING, logging.ERROR):
            module_name, function_name = self._get_caller_info(stack_level)
            msg = f"{module_name}.{function_name}: {msg}"
            if record.exc_info:
                msg += "\n" + self.formatException(record.exc_info)

        asctime = self.formatTime(record, self.datefmt)

        # Replace the placeholders in the format string with the actual values
        return log_fmt % {"asctime": asctime, "levelname": record.levelname, "message": msg}


class Logger:
    """Manage logging"""

    os.makedirs("log", exist_ok=True)
    _logger_level = "DEBUG"
    _log_contents = io.StringIO()
    _current_log_file_path = "log/log.txt"
    _output = ""  # intercepted output from stdout and stderr
    string_handler = None
    file_handler = None
    console_handler = None
    logger = None

    @staticmethod
    def debug(data: str):
        if Logger.logger is None:
            Logger.init()
        Logger.logger.debug(data)

    @staticmethod
    def info(data: str):
        if Logger.logger is None:
            Logger.init()
        Logger.logger.info(data)

    @staticmethod
    def warning(data: str):
        if Logger.logger is None:
            Logger.init()
        Logger.logger.warning(data)

    @staticmethod
    def error(data: str):
        if Logger.logger is None:
            Logger.init()
        Logger.logger.error(data)

    @staticmethod
    def exception(data: str):
        if Logger.logger is None:
            Logger.init()
        Logger.logger.exception(data)

    @staticmethod
    def init(lvl: str = "DEBUG"):
        """
        Setup logger for StringIO, console and file handler
        """
        Logger._logger_level = lvl.upper()

        if Logger.logger is not None:
            for hdlr in Logger.logger.handlers[:]:  # remove all old handlers
                Logger.logger.removeHandler(hdlr)

        # Create the logger
        Logger.logger = logging.getLogger("d4lf")
        for hdlr in Logger.logger.handlers:
            Logger.logger.removeHandler(hdlr)
        Logger.logger.setLevel(Logger._logger_level)
        Logger.logger.propagate = False

        # Setup the StringIO handler
        Logger._log_contents = io.StringIO()
        Logger.string_handler = logging.StreamHandler(Logger._log_contents)
        Logger.string_handler.setLevel(Logger._logger_level)

        # Setup the console handler
        Logger.console_handler = logging.StreamHandler(sys.stdout)
        Logger.console_handler.setLevel(Logger._logger_level)

        # Setup the file handler
        Logger.file_handler = logging.FileHandler(Logger._current_log_file_path, "a")
        Logger.file_handler.setLevel(Logger._logger_level)

        # Optionally add a formatter
        _format = CustomFormatter()
        Logger.string_handler.setFormatter(_format)
        Logger.console_handler.setFormatter(_format)
        Logger.file_handler.setFormatter(logging.Formatter(_format._format))

        # Add the handler to the logger
        Logger.logger.addHandler(Logger.string_handler)
        Logger.logger.addHandler(Logger.console_handler)
        Logger.logger.addHandler(Logger.file_handler)

    @staticmethod
    def remove_file_logger(delete_current_log: bool = False):
        """
        Remove the file logger to not write output to a log file
        """
        Logger.logger.removeHandler(Logger.file_handler)
        if delete_current_log and os.path.exists(Logger._current_log_file_path):
            try:
                os.remove(Logger._current_log_file_path)
            except PermissionError:
                warnings.warn(f"Could not remove {Logger._current_log_file_path}, permission denied", stacklevel=2)
