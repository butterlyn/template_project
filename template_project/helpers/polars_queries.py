# standard imports
from datetime import (
    datetime,
    timedelta,
)
# third-party imports
import polars as pl
from typing import (
    cast,
    Final,
)


def cast_excel_1900_date_system_datetime(
    datetime_column: pl.Expr | str,
) -> pl.Expr:
    """
    Casts data type of Polars Series from days-since-1900-01-01 float
    into datetime[ms].

    Args:
        datetime_column (pl.Expr | str): The column name to be converted.
        If already a Polars Expr, it is returned as is.

    Returns:
        pl.Expr: The datetime column as a Polars Expr.

    Example:
        >>> df = pl.DataFrame({
        ...     "date": [1, 2, 3],
        ... })
        >>> cast_excel_1900_date_system_datetime("date")
        >>> cast_excel_1900_date_system_datetime(pl.col("date"))

    Note:
        This function corrects for 1900 being misinterpreted as a leap
        year in Excel's default 1900 date system (plus some other
        unaccounted for error in 1900 date system).
    """
    SECONDS_IN_DAY: Final[int] = 60 * 60 * 24

    # correction for 1900 being misinterpreted as a leap year in Excel's
    # default 1900 date system
    # (plus some other unaccounted for error in 1900 date system)
    CORRECTION_IN_DAYS: Final[float] = -2
    CORRECTION_IN_SECONDS: Final[float] = CORRECTION_IN_DAYS * SECONDS_IN_DAY

    # if passes as a string, convert to Polars Expr
    datetime_column_expr: pl.Expr = (
        pl.col(cast(str, datetime_column))
        if isinstance(datetime_column, str)
        else cast(pl.Expr, datetime_column)
    )

    # convert arguments from days to seconds
    seconds_since_1900_epoch: pl.Expr = datetime_column_expr.mul(SECONDS_IN_DAY)

    # get time difference between 1970 & 1900 epochs in seconds
    epoch_1970: datetime = datetime(year=1970, month=1, day=1)
    epoch_1900: datetime = datetime(year=1900, month=1, day=1)
    timedelta_epochs_1900_1970: timedelta = epoch_1970 - epoch_1900
    seconds_between_epochs_1900_1970: float = \
        timedelta_epochs_1900_1970.total_seconds()

    # calculate seconds since 1970 epoch
    seconds_since_1970_epoch: pl.Expr = (
        seconds_since_1900_epoch
        .sub(seconds_between_epochs_1900_1970)
        .add(CORRECTION_IN_SECONDS)
    )

    # return datetime Polars Series based on seconds since 1970 epoch
    return pl.from_epoch(
        column=seconds_since_1970_epoch,
        time_unit='s'
    )
