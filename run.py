import logging
from src.template_project.helpers.logger import getRichLogger

getRichLogger(
    logging_level="DEBUG",
    traceback_show_locals=True,
    traceback_extra_lines=10,
    traceback_suppressed_modules=(),
)
