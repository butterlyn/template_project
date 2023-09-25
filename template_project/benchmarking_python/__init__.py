from ..helpers import getRichLogger as _getRichLogger
from .utils import LoadersDictTypeHint
from .benchmarks import loaders_dict

__all__: list[str] = []

_getRichLogger(
    logging_level="DEBUG",
    logger_name=__name__,
    traceback_show_locals=True,
    traceback_extra_lines=10,
    traceback_suppressed_modules=(),
)
