import logging
import pytest
from template_project.helpers.rich_logger import getRichLogger
from rich.logging import RichHandler

# ~~~ test default ~~~


# def test_getRichLogger_default():
#     getRichLogger()
#     assert isinstance(logging.getLogger(), logging.Logger)
#     assert logging.getLogger().level == logging.NOTSET
#     assert isinstance(logging.getLogger().handlers, logging.Handler)
#     assert isinstance(logging.getLogger().handlers[0], RichHandler)
#     assert logging.getLogger().handlers[0].formatter._fmt == "%(message)s"


# # ~~~ test full set of non default arguments ~~~

# def test_getRichLogger_custom():
#     getRichLogger(
#         logging_level=logging.WARNING,
#         logger_name="test_logger2",
#         enable_rich_logger=False,
#         rich_logger_format="%(name)s %(message)s",
#         non_rich_logger_format="%(message)s",
#         traceback_show_locals=False,
#         traceback_hide_dunder_locals=False,
#         traceback_hide_sunder_locals=False,
#         traceback_extra_lines=100,
#         traceback_suppressed_modules=[pytest],
#         additional_handlers=logging.FileHandler("test.log"),
#     )
#     assert isinstance(logging.getLogger(), logging.Logger)
#     assert logging.getLogger().level == logging.WARNING
#     assert logging.getLogger().name == "test_logger2"
#     assert len(logging.getLogger().handlers) == 2

# # ~~~ test each argument in detail ~~~


# @pytest.mark.parametrize(
#     "logging_level",
#     [
#         logging.DEBUG,
#         logging.INFO,
#         logging.WARNING,
#         logging.ERROR,
#         logging.CRITICAL,
#         0,
#         10,
#         20,
#         30,
#         40,
#     ]
# )
# def test_getRichLogger_level(logging_level):
#     getRichLogger(logging_level=logging_level)
#     assert logging.getLogger().level == logging_level


# def test_getRichLogger_name():
#     getRichLogger(logger_name="test_logger")
#     assert logging.getLogger().name == "test_logger"


# @pytest.mark.parametrize(
#     "additional_handlers",
#     [
#         logging.FileHandler("test.log"),
#         [logging.FileHandler("test.log")],
#     ]
# )
# def test_getRichLogger_one_additional_handler(additional_handlers):
#     getRichLogger(additional_handlers=logging.FileHandler("test.log"))
#     assert len(logging.getLogger().handlers) == 2


# def test_getRichLogger_multiple_additional_handlers():
#     getRichLogger(additional_handlers=[logging.FileHandler(
#         "test.log"), logging.FileHandler("test2.log")])
#     assert len(logging.getLogger().handlers) == 3


# # ~~~ test handled exceptions ~~~


# def test_getRichLogger_raise_TypeError():
#     with pytest.raises(TypeError):
#         getRichLogger(additional_handlers="not a handler")
