from typing import Iterable
from types import ModuleType
import logging
from rich.logging import RichHandler
from rich import traceback


def getRichLogger(
    logging_level: str | int = "NOTSET",
    logger_name: str = __name__,
    enable_rich_logger: bool = True,
    rich_logger_format: str = "%(message)s",
    non_rich_logger_format: str = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    traceback_show_locals: bool = True,
    traceback_hide_dunder_locals: bool = True,
    traceback_hide_sunder_locals: bool = True,
    traceback_extra_lines: int = 10,
    traceback_suppressed_modules: Iterable[ModuleType] = (),
    additional_handlers: logging.Handler | Iterable[logging.Handler] | None = None,
) -> logging.Logger:
    """
    Substitute for logging.getLogger(), but pre-configured as rich logger with rich traceback.

    Parameters
    ----------
    logging_level : str or int, optional
        The logging level to use. Defaults to 'NOTSET'.
    logger_name : str, optional
        The name of the logger. Defaults to __name__.
    enable_rich_logger : bool, optional
        Whether to enable the rich logger and rich traceback or basic. Defaults to True.
    rich_logger_format : str, optional
        The format string to use for the rich logger. Defaults to "%(message)s".
    non_rich_logger_format : str, optional
        The format string to use for the non-rich logger. Defaults to "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s".
    traceback_show_locals : bool, optional
        Whether to show local variables in tracebacks. Defaults to True.
    traceback_hide_dunder_locals : bool, optional
        Whether to hide dunder variables in tracebacks. Defaults to True.
    traceback_hide_sunder_locals : bool, optional
        Whether to hide sunder variables in tracebacks. Defaults to True.
    traceback_extra_lines : int, optional
        The number of extra lines to show in tracebacks. Defaults to 10.
    traceback_suppressed_modules : Iterable[ModuleType], optional
        The modules to suppress in tracebacks (e.g., pandas). Defaults to ().
    additional_handlers : logging.Handler or list[logging.Handler], optional
        Additional logging handlers to use. Defaults to [].

    Returns
    -------
    logging.Logger
        The configured logger.

    Raises
    ------
    TypeError
        If additional_handlers is not a logging.Handler, Iterable[logging.Handler], or None.

    Example
    -------
    >>> import logging
    >>> from logger import getRichLogger
    >>> getRichLogger(loggin_level='DEBUG')
    >>> logging.debug("this is a rich debug message! the traceback of the below unhandled exception is also rich")
    >>> 1/0
    """

    # ~~~~~ helper functions ~~~~~

    def _install_rich_traceback() -> None:
        """Installs rich traceback for unhandled exceptions."""
        traceback.install(
            extra_lines=traceback_extra_lines,
            theme='monokai',
            show_locals=traceback_show_locals,
            locals_hide_dunder=traceback_hide_dunder_locals,
            locals_hide_sunder=traceback_hide_sunder_locals,
            suppress=traceback_suppressed_modules,
        )

    def _convert_additional_handlers_to_list() -> list[logging.Handler]:
        """Convert additional_handlers to list for combining with rich handler"""
        additional_handlers_list: list[logging.Handler] = (
            [additional_handlers] if isinstance(additional_handlers, logging.Handler)
            else list(additional_handlers) if isinstance(additional_handlers, Iterable)
            else [] if additional_handlers is None
            else TypeError(f"additional_handlers must be a logging.Handler, Iterable[logging.Handler], or None, not {type(additional_handlers)}")
        )
        return additional_handlers_list

    def _get_rich_handler() -> list[logging.Handler]:
        """Create rich handler in a list for combining with additional handlers"""
        return [
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
        ]

    # ~~~~~ business logic ~~~~~

    # Installs rich traceback for unhandled exceptions if enabled
    if enable_rich_logger:
        _install_rich_traceback()

    # Set the logger message format based on whether rich logger is enabled
    format: str = (
        rich_logger_format if enable_rich_logger
        else non_rich_logger_format
    )

    # Combine the rich handler with any additional handlers
    rich_handler = _get_rich_handler()
    additional_handlers_list = _convert_additional_handlers_to_list()
    all_handlers = (
        rich_handler + additional_handlers_list if enable_rich_logger
        else additional_handlers_list
    )

    # Configure the logger with the handlers
    logging.basicConfig(
        level=logging.getLevelName(logging_level),
        format=format,
        handlers=all_handlers,
    )

    # Get the logger and return it
    return logging.getLogger(logger_name)
