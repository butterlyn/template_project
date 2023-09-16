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
