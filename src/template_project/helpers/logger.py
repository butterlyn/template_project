from typing import Iterable
from types import ModuleType
import logging
from rich.logging import RichHandler
from rich import traceback


def getRichLogger(
    logging_level: str | int = 'NOTSET',
    logger_name: str = __name__,
    enable_rich_logger: bool = True,
    rich_logger_format: str = "%(message)s",
    non_rich_logger_format: str = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    traceback_show_locals: bool = True,
    traceback_hide_dunder_locals: bool = True,
    traceback_hide_sunder_locals: bool = True,
    traceback_extra_lines: int = 5,
    traceback_suppressed_modules: Iterable[ModuleType] = (),
    additional_handlers: logging.Handler | Iterable[logging.Handler] | None = None,
) -> logging.Logger:
    """
    Configures a logger, defaults to rich logger with rich traceback.
    Toggle enable_rich_logger off for basic logger with basic traceback.

    Args:
        logging_level (str | int, optional): The logging level to use. Defaults to 'NOTSET'.
        logger_name (str, optional): The name of the logger. Defaults to __name__.
        enable_rich_logger (bool, optional): Whether to enable the rich logger. Defaults to True.
        rich_logger_format (str, optional): The format string to use for the rich logger. Defaults to "%(message)s".
        non_rich_logger_format (str, optional): The format string to use for the non-rich logger. Defaults to "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s".
        traceback_show_locals (bool, optional): Whether to show local variables in rich tracebacks. Defaults to True.
        traceback_hide_dunder_locals (bool, optional): Whether to hide dunder variables in rich tracebacks. Defaults to True.
        traceback_hide_sunder_locals (bool, optional): Whether to hide sunder variables in rich tracebacks. Defaults to True.
        traceback_extra_lines (int, optional): The number of extra lines to show in rich tracebacks. Defaults to 5.
        traceback_suppressed_modules (Iterable[ModuleType], optional): The modules to suppress in rich tracebacks (e.g., pandas). Defaults to ().
        additional_handlers (logging.Handler | list[logging.Handler], optional): Additional logging handlers to use. Defaults to [].

    Returns:
        logging.Logger: The configured logger.
    """

    # If rich logger enabled, install rich traceback for unhandled expections
    if enable_rich_logger:
        traceback.install(
            extra_lines=traceback_extra_lines,
            theme='monokai',
            show_locals=traceback_show_locals,
            locals_hide_dunder=traceback_hide_dunder_locals,
            locals_hide_sunder=traceback_hide_sunder_locals,
            suppress=traceback_suppressed_modules,
        )

    # Set the logger message format based on whether rich logger is enabled
    format: str = rich_logger_format if enable_rich_logger else non_rich_logger_format

    # Convert additional_handlers to list if not already a list
    if isinstance(additional_handlers, logging.Handler):  # for single handlers
        additional_handlers = [additional_handlers]
    elif isinstance(additional_handlers, Iterable) and not isinstance(additional_handlers, str):
        additional_handlers = list(additional_handlers)  # for non-list iterables
    elif additional_handlers is None:
        additional_handlers = []

    # Combine rich handler with any provided additional handlers
    handlers: Iterable[logging.Handler] | None = [
        RichHandler(
            level=logging.getLevelName(logging_level),
            omit_repeated_times=False,
            rich_tracebacks=enable_rich_logger,
            tracebacks_extra_lines=traceback_extra_lines,
            tracebacks_theme="monokai",
            tracebacks_word_wrap=False,
            tracebacks_show_locals=traceback_show_locals,
            tracebacks_suppress=traceback_suppressed_modules,
            log_time_format="[%Y-%m-%d %H:%M:%S] ",
        )
    ] + additional_handlers if enable_rich_logger else additional_handlers if additional_handlers else None

    # Configure the logger
    logging.basicConfig(
        level=logging.getLevelName(logging_level),
        format=format,
        handlers=handlers,
    )

    # Get the logger object
    logger: logging.Logger = logging.getLogger(logger_name)

    return logger
