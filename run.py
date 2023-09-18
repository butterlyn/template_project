import logging
from template_project.helpers.rich_logger import getRichLogger
from src.template_project.library_books import main


getRichLogger(
    logging_level="DEBUG",
    traceback_show_locals=False,
    traceback_extra_lines=10,
    traceback_suppressed_modules=(),
)
logging.debug("Rich logger and rich traceback enabled")

main()
a=1