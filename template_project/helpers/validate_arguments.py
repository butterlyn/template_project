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

    # total number of validations to perform
    total_validations_count: int = len(argument_validation_checks)

    current_validation_index: int = 0
    passed_count: int = 0
    failed_count: int = 0
    # check if all arguments are valid, log and store errors if not
    for arugment_validation_check in argument_validation_checks:
        current_validation_index += 1
        is_valid, error_message = arugment_validation_check
        if is_valid:
            passed_count += 1
        else:
            error: Exception = AttributeError(error_message)
            logging.error(error)
            all_errors.append(error)
            failed_count += 1
        logging.debug(f"{current_validation_index}/{total_validations_count} - {passed_count} passed, {failed_count} failed. Validating arugments for initialising {class_name}.")

    # raise all errors if any occurred
    if not all_errors:
        return
    if len(all_errors) == 1:
        raise all_errors[0]
    raise ExceptionGroup(
        f"{len(all_errors)} attribute errors occurred when initialising {class_name}",
        all_errors,
    )


if __name__ == "__main__":
    import dataclasses

    @dataclasses.dataclass(
        frozen=True,
        slots=True,
        kw_only=True,
    )
    class MyClass:
        """class_name class"""
        instance_attribute_1: str
        instance_attribute_2: int

        @property
        def composed_attribute_1(self) -> float:
            return float(self.instance_attribute_2)

        @property
        def _class_name(self) -> str:
            return type(self).__name__

        def __post_init__(self) -> None:
            """Validate arguments after initialisation"""
            logging.debug(f"Validating {self._class_name} arguments...")
            validate_arguments(
                class_name=self._class_name,
                argument_validation_checks=[
                    # validate instance_attribute_1
                    (
                        isinstance(self.instance_attribute_1, str),
                        f"{self.instance_attribute_1} should be a string!.",
                    ),
                    # validate instance_attribute_2
                    (
                        isinstance(self.instance_attribute_2, int),
                        f"{self.instance_attribute_2} should be a integer!.",
                    ),
                ],
            )

    logging.debug("Creating instance of MyClass with incorrect arguments...")
    my_class = MyClass(
        instance_attribute_1="string",
        instance_attribute_2=1.0,  # type: ignore
    )
