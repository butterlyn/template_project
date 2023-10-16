# standard imports
import datetime
# third-party imports
import polars as pl


def cast_excel_1900_date_system_to_datetime(
    days_since_1900_epoch: pl.Series,
    correction_in_days: float = -2,  # correction for 1900 being misinterpreted as a leap year in Excel's default 1900 date system (plus some other unaccounted for error in 1900 date system)
) -> pl.Series:
    """Casts data type of Polars Series from days-since-1900-01-01 float into datetime[ms]."""
    SECONDS_IN_DAY: int = 60 * 60 * 24

    # convert arguments from days to seconds
    seconds_since_1900_epoch: pl.Series = days_since_1900_epoch * SECONDS_IN_DAY
    correction_in_seconds: float = correction_in_days * SECONDS_IN_DAY

    # get time difference between 1970 & 1900 epochs in seconds
    epoch_1970: datetime.datetime = datetime.datetime(year=1970, month=1, day=1)
    epoch_1900: datetime.datetime = datetime.datetime(year=1900, month=1, day=1)
    datetime_delta_epochs_1900_1970: datetime.timedelta = epoch_1970 - epoch_1900
    seconds_between_epochs_1900_1970: float = datetime_delta_epochs_1900_1970.total_seconds()

    # calculate seconds since 1970 epoch
    seconds_since_1970_epoch: pl.Series = seconds_since_1900_epoch - seconds_between_epochs_1900_1970 + correction_in_seconds

    # return datetime Polars Series based on seconds since 1970 epoch
    return pl.from_epoch(seconds_since_1970_epoch, time_unit='s')
