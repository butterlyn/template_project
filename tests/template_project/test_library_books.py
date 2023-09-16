from contextlib import nullcontext as does_not_raise
import pytest
from src.template_project.library_books import (
    Book,
    BookDefaults,
)
from exceptiongroup import ExceptionGroup


def test_book_defaults():
    assert BookDefaults.NAME_MINIMUM_LENGTH.value >= 0
    assert BookDefaults.NAME_MINIMUM_LENGTH.value >= 0


@pytest.mark.parametrize(
    "book_name_difference, book_page_count_difference, name_letter_capitalisation, expected_raise",
    [
        (10, 10, "A", does_not_raise()),
        (1, 1, "A", does_not_raise()),
        (0, 0, "A", does_not_raise()),
        (-1, 0, "A", pytest.raises(ExceptionGroup)),
        (0, -1, "A", pytest.raises(ExceptionGroup)),
        (0, -10, "A", pytest.raises(ExceptionGroup)),
        (-10, 0, "A", pytest.raises(ExceptionGroup)),
        (10, 10, "a", pytest.raises(ExceptionGroup)),
        (10, 10, "9", pytest.raises(ExceptionGroup)),
        (10, 10, ";", pytest.raises(ExceptionGroup)),
        (-10, -10, "A", pytest.raises(ExceptionGroup)),
    ],
)
@pytest.mark.parametrize(
    "minimum_page_count, minimum_name_length",
    [
        (0, 5),
        (1, 5),
        (5, 5),
        (5, 0),
        (5, 1),
        (5, 5),
    ],
)
def test_book_argument_validation_error_handling(
    minimum_page_count,
    minimum_name_length,
    book_name_difference,
    book_page_count_difference,
    name_letter_capitalisation,
    expected_raise,
):
    # set test values
    book_name_length = minimum_name_length + book_name_difference
    if book_name_length < 0:
        return
    book_name = name_letter_capitalisation * book_name_length
    book_page_count = minimum_page_count + book_page_count_difference
    # test
    with expected_raise:
        book = Book(
            book_name=book_name,
            book_page_count=book_page_count,
            _BOOK_MINIMUM_PAGE_COUNT=minimum_page_count,
            _BOOK_NAME_MINIMUM_LENGTH=minimum_name_length,
        )
        assert book.book_name == book_name
        assert book.book_page_count == book_page_count
        assert book._BOOK_MINIMUM_PAGE_COUNT == minimum_page_count
        assert book._BOOK_NAME_MINIMUM_LENGTH == minimum_name_length
