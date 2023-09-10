from typing import Iterable
from types import ModuleType
import logging
from rich.logging import RichHandler
from rich import traceback

# ~~~~~ configure logger ~~~~~

# set LOGGING_LEVEL to one of the following integers:
# 'NOTSET' -> 0  # same as DEBUG but can be overridden by parent logger
# 'DEBUG' -> 10
# 'INFO' -> 20
# 'WARN' -> 30
# 'ERROR' -> 40
# 'CRITICAL' -> 50
LOGGING_LEVEL: int = 0
LOGGER_NAME: str = __name__
ADDITIONAL_HANDLERS: list[logging.Handler] = []
ENABLE_RICH_TRACBACK: bool = True

# only used if ENABLE_RICH_TRACBACK is True
TRACEBACK_SHOW_LOCALS: bool = True
TRACKBACK_HIDE_DUNDER_LOCALS: bool = True
TRACKBACK_HIDE_SUNDER_LOCALS: bool = True
TRACEBACK_EXTRA_LINES: int = 3  # if in doubt, set to 3
TRACEBACK_SUPPRESSED_MODULES: Iterable[ModuleType] = (
    # pd,
)

# ~~~~~ set logger ~~~~~

# setup the rich traceback for unhandled exceptions

if ENABLE_RICH_TRACBACK:
    traceback.install(
        extra_lines=TRACEBACK_EXTRA_LINES,  # default 3
        theme='monokai',
        show_locals=TRACEBACK_SHOW_LOCALS,  # default False
        locals_hide_dunder=TRACKBACK_HIDE_DUNDER_LOCALS,  # default True
        locals_hide_sunder=TRACKBACK_HIDE_SUNDER_LOCALS,  # default True
        suppress=TRACEBACK_SUPPRESSED_MODULES,
    )
    # append rich handler to handlers
    handlers = [
        RichHandler(
            level=LOGGING_LEVEL,
            omit_repeated_times=False,  # default True
            rich_tracebacks=ENABLE_RICH_TRACBACK,
            tracebacks_extra_lines=TRACEBACK_EXTRA_LINES,
            tracebacks_theme="monokai",
            tracebacks_word_wrap=False,  # default True
            tracebacks_show_locals=TRACEBACK_SHOW_LOCALS,  # default false
            tracebacks_suppress=TRACEBACK_SUPPRESSED_MODULES,
            log_time_format="[%Y-%m-%d %H:%M:%S] ",
        )
    ] + ADDITIONAL_HANDLERS
else:
    handlers = ADDITIONAL_HANDLERS

# setup rich logger and rich handled traceback. I.e., for`logger.exception(e)`
logging.basicConfig(
    level=LOGGING_LEVEL,
    format="%(message)s",
    handlers=handlers,
)

# Create a logger
logger = logging.getLogger(LOGGER_NAME)

# ~~~~~ code ~~~~~
