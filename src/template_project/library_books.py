# standard library imports
import logging
from dataclasses import field
import dataclasses
from typing import (
    Protocol,
    Iterable,
)
from types import ModuleType
from enum import Enum
import logging
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


getRichLogger(
    logging_level="DEBUG",
    traceback_show_locals=True,
    traceback_extra_lines=10,
    traceback_suppressed_modules=(),
)
logging.debug("Rich logger and rich traceback enabled")


# ~~~~~ configuration  and global variables ~~~~~


class BookDefaults(Enum):
    MINIMUM_PAGE_COUNT: int = 1
    NAME_MINIMUM_LENGTH: int = 1


# ~~~~~ helpers ~~~~~

import logging
from exceptiongroup import ExceptionGroup


def validate_arguments(
    class_name: str,
    argument_validation_checks: list[tuple[bool, str]],
) -> None:
    """
    Validate class instance arguments and raise and log errors if any occur.
    Intended to be used in `__post_init__` methods.

    Parameters
    ----------
    class_name : str
        The name of the class being initialized. If in doubt, use `type(self).__name__`.
    argument_validation_checks : list[tuple[bool, str]]
        A list of tuples containing a boolean for passing a conditional statement indicating whether the argument is valid and an error message if it is not.

    Raises
    ------
    ExceptionGroup
        If any errors occurred during argument validation, an ExceptionGroup is raised containing all the errors.

    Examples
    -----
    >>> validate_arguments_raise_and_log_errors(
    ...     "Book",
    ...     [
    ...         (len(book_name) >= Book.BOOK_NAME_MINIMUM_LENGTH, f"Book name must be at least {Book.BOOK_NAME_MINIMUM_LENGTH} characters long"),
    ...         (book_page_count >= Book.BOOK_MINIMUM_PAGE_COUNT, f"Book must have at least {Book.BOOK_MINIMUM_PAGE_COUNT} pages"),
    ...     ],
    ... )
    """
    # variable to store any errors that occur
    all_errors: list[Exception] = []

    # check if all arguments are valid, log and store errors if not
    for arugment_validation_check in argument_validation_checks:
        is_valid, error_message = arugment_validation_check
        if is_valid:
            continue
        error: Exception = AttributeError(error_message)
        logging.error(error)
        all_errors.append(error)

    # raise all errors if any occurred
    if not all_errors:
        return
    raise ExceptionGroup(
        f"{len(all_errors)} attribute errors occurred when initialising {class_name}",
        all_errors,
    )



# ~~~~~ simple dataclasses ~~~~~


@dataclasses.dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class Book:
    """Book class"""

    # ~~~~~ instance attributes ~~~~~
    book_name: str
    book_page_count: int
    # ~~~~~ composed attributes (properties) ~~~~~
    ...
    # ~~~~~ constants ~~~~~
    _BOOK_MINIMUM_PAGE_COUNT: int = BookDefaults.MINIMUM_PAGE_COUNT.value
    _BOOK_NAME_MINIMUM_LENGTH: int = BookDefaults.NAME_MINIMUM_LENGTH.value

    def __post_init__(self) -> None:
        """Validate arguments after initialisation"""
        logging.debug(f"Validating {type(self).__name__} arguments...")
        validate_arguments(
            class_name=type(self).__name__,
            argument_validation_checks=[
                # validate book_name
                (
                    (
                        self.book_name[0].isupper()
                        if len(self.book_name) > 0
                        else True
                        if self._BOOK_NAME_MINIMUM_LENGTH == 0
                        else False
                    ),
                    f"{self.book_name} first letter must be capitalised.",
                ),
                (
                    len(self.book_name) >= self._BOOK_NAME_MINIMUM_LENGTH,
                    f"{self.book_name} does not meet the minimum length of {self._BOOK_NAME_MINIMUM_LENGTH}.",
                ),
                # validate book_page_count
                (
                    self.book_page_count >= self._BOOK_MINIMUM_PAGE_COUNT,
                    f"{self.book_page_count} does not meet the minimum page count of {self._BOOK_MINIMUM_PAGE_COUNT}.",
                ),
            ],
        )


# ~~~~~ composed dataclasses ~~~~~

...


# ~~~~~ abc, protocol classes, base classes ~~~~~


class GiveBookCapable(Protocol):
    def give_book(self, book_to_add: Book) -> Book | None:
        pass


class ReceiveBookCapable(Protocol):
    def receive_book(self, book_to_loan: Book | None) -> None:
        pass


# ~~~~~ behaviour-oriented classes ~~~~~


class Library:
    """Library class"""

    def __init__(
        self,
        library_book_collection: list[Book] = field(default_factory=list),
    ):
        # store public instance attributes
        self._library_book_collection = library_book_collection
        # store private instance attributes
        ...
        # store public non-constructor dependent attributes
        self._books_on_loan: list[Book] = []
        # store private non-constructor dependent attributes
        ...

    # ~~~~~ set attributes ~~~~~

    # set simple attributes

    @property
    def library_book_collection(self) -> list[Book]:
        return self._library_book_collection

    @property
    def books_on_loan(self) -> list[Book]:
        return self._books_on_loan

    # set composed attributes

    ...

    # set dunder attributes

    def __str__(self) -> str:
        return f"{type(self).__name__}"

    # ~~~~~ helper class methods ~~~~~

    ...

    # ~~~~~ methods ~~~~~

    def give_book(self, book_to_give: Book) -> Book | None:
        """Give book from library book collection"""
        if book_to_give in self.library_book_collection:
            self.books_on_loan.append(book_to_give)
            return book_to_give
        elif book_to_give in self.books_on_loan:
            logging.warning("Book is already on loan")
            return None
        else:
            logging.warning("Attempted to loan book not in collection.")
            return None

    def receive_book(self, book_received: Book | None) -> None:
        if not book_received:
            return
        elif book_received in self.books_on_loan:
            self.books_on_loan.remove(book_received)
        else:
            logging.warning(
                "Received book not on loan. Adding to library collection.")
            self.library_book_collection.append(book_received)


class Person:
    """Person class"""

    def __init__(
        self,
        name: str,
        books_in_possession: list[Book] = field(default_factory=list),
    ) -> None:
        self._name: str = name
        self._books_in_possession: list[Book] = books_in_possession

    # ~~~~~ set attributes ~~~~~

    ##
    @property
    def books_in_possession(self) -> list[Book]:
        return self._books_in_possession

    ##
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        error_message = f"Attempted to overwrite {type(self).__name__}'s name from {self.name} to {value}. Name cannot be overwritten."
        error = AttributeError(error_message)
        logging.error(error)
        raise error

    @name.deleter
    def name(self) -> None:
        error_message = f"Attempted to delete {type(self).__name__}'s name '{self.name}'. Names cannot be deleted."
        error = AttributeError(error_message)
        logging.error(error)
        raise error

    # ~~~~~ helper methods ~~~~~

    ...

    # ~~~~~ methods ~~~~~

    def receive_book(self, book_to_receive: Book | None) -> None:
        """Add book to possession of person"""
        (
            self.books_in_possession.append(book_to_receive)
            if book_to_receive
            else logging.warning(
                f"{book_to_receive} not added to possession of {self.name}."
            )
        )

    def give_book(self, book_to_give: Book) -> Book | None:
        """Give book from books in possession of person"""
        if book_to_give in self.books_in_possession:
            self.books_in_possession.remove(book_to_give)
            return book_to_give
        else:
            logging.warning(
                f"{self.name} does not have {book_to_give} in their possession."
            )
            return None


# ~~~~~ composed functions ~~~~~
def transfer_book(
    book_giver: GiveBookCapable,
    book_receiver: ReceiveBookCapable,
    books: list[Book],
) -> None:
    """Loan one or more books from library to person"""
    for book in books:
        book_receiver.receive_book(
            book_giver.give_book(book),
        )

# @profile
def main() -> None:
    # ~~~~~ initialise classes ~~~~~
    math_book_1: Book = Book(
        book_name="Mathematics for Engineers",
        book_page_count=100,
    )

    cook_book_12: Book = Book(
        book_name="Cooking for Dummies",
        book_page_count=35,
    )

    local_library: Library = Library(
        library_book_collection=[
            math_book_1,
            math_book_1,
            cook_book_12,
        ],
    )

    person_stacy: Person = Person(
        name="Stacy",
        books_in_possession=[],
    )

    # ~~~~~ business logic ~~~~~

    books_to_transfer: list[Book] = [
        cook_book_12,
        math_book_1,
    ]

    transfer_book(
        book_giver=local_library,
        book_receiver=person_stacy,
        books=books_to_transfer,
    )

    logging.info(
        f"{person_stacy.name} has:\n{person_stacy.books_in_possession}.")
    logging.info(
        f"{local_library} has:\n{local_library.books_on_loan} books on loan.")
    logging.info(
        f"{local_library} has:\n{local_library.library_book_collection} books in collection.")

if __name__ == "__main__":
    # from pycallgraph import PyCallGraph
    # from pycallgraph.output import GraphvizOutput
    # with PyCallGraph(output=GraphvizOutput()):
    main()
    Book(book_name="Alphred's Book", book_page_count=120)
    a=1