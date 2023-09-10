from typing import Iterable
from types import ModuleType
import logging
from rich.logging import RichHandler
from rich import traceback


def configure_logger(
    logging_level: str | int = 'NOTSET',
    logger_name: str = __name__,
    additional_handlers: logging.Handler | list[logging.Handler] = [],
    enable_rich_logger: bool = True,
    rich_logger_format: str = "%(message)s",
    non_rich_logger_format: str = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    traceback_show_locals: bool = True,
    traceback_hide_dunder_locals: bool = True,
    traceback_hide_sunder_locals: bool = True,
    traceback_extra_lines: int = 5,
    traceback_suppressed_modules: Iterable[ModuleType] = (),
) -> logging.Logger:

    if enable_rich_logger:
        traceback.install(
            extra_lines=traceback_extra_lines,
            theme='monokai',
            show_locals=traceback_show_locals,
            locals_hide_dunder=traceback_hide_dunder_locals,
            locals_hide_sunder=traceback_hide_sunder_locals,
            suppress=traceback_suppressed_modules,
        )

    format: str = rich_logger_format if enable_rich_logger else non_rich_logger_format

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

    logging.basicConfig(
        level=logging.getLevelName(logging_level),
        format=format,
        handlers=handlers,
    )

    logger: logging.Logger = logging.getLogger(logger_name)

    return logger


logger = configure_logger()
