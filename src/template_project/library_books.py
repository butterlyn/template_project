import logging
from dataclasses import field
import dataclasses
from typing import Protocol
from enum import Enum
from memory_profiler import profile
from .helpers.validate_arguments import validate_arguments
from .helpers.logger import getRichLogger

# ~~~~~ evaluation ~~~~~
# import heartrate
# heartrate.trace(browser=True)


# ~~~~~ logging ~~~~~


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

...


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
