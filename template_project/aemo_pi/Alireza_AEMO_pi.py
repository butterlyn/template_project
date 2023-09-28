# %%
# Importing Libraries

from typing import List, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import aemo_pi

# %%
# Global Variables

pi = aemo_pi.connect("PIProd")

# %%
# Functions


# dates for pi
def _func_pi_dates(
    study_date: str, interval: str, before_study_date: str, after_study_date: str
) -> Tuple[str, str, str]:
    """
    Calculates the start and end datetime for the given study date, interval, before and after study date.

    Args:
    study_date (str): The study date in the format of "YYYY/MM/DD HHMM".
    interval (str): The interval as a string (e.g., '1h').
    before_study_date (str): The time before the study date in the format of "Xm".
    after_study_date (str): The time after the study date in the format of "Xm".

    Returns:
    Tuple[str, str, str]: A tuple containing startdatetime, enddatetime and interval.
    """
    study_date = study_date.replace("-", "/")
    study_date = datetime.strptime(study_date, "%Y/%m/%d %H%M")
    startdatetime = study_date - timedelta(hours=0, minutes=int(before_study_date[:-1]))
    enddatetime = study_date + timedelta(hours=0, minutes=int(after_study_date[:-1]))
    startdatetime = startdatetime.strftime("%Y-%m-%d %H:%M:%S")
    enddatetime = enddatetime.strftime("%Y-%m-%d %H:%M:%S")
    interval = interval
    return startdatetime, enddatetime, interval


def _check_data_for_nan(df: pd.DataFrame) -> int:
    """
    Check if there are any NaN values in the given dataframe.

    Args:
    df (pandas.DataFrame): The dataframe to check for NaN values.

    Returns:
    int: 1 if there are no NaN values, 0 otherwise.
    """
    try:
        no_nan_values = 1
        for i in range(len(df)):
            for column in df.columns:
                if np.isnan(df[column].iloc[i]):
                    print(f"{df.index[i]} - {column}: {df[column].iloc[i]}")
                    no_nan_values = 0
        return no_nan_values
    except Exception as exception:
        raise ValueError(f"Error in _check_data_for_nan: {exception}") from exception


def pull_pi_data(
    pi_tags_list: List[str],
    study_date: str,
    interval: str,
    before_study_date: str,
    after_study_date: str,
    pi_already_connected: bool = False,
) -> Tuple[pd.DataFrame, int]:
    """
    Pulls data from aemo_pi.

    Args:
    pi_tags_list (List[str]): A list of aemo-pi tags to be pulled.
    study_date (str): The study date in the format of "YYYY/MM/DD HHMM".
    interval (str): The interval as a string (e.g., '1h').
    before_study_date (str): The time before the study date in the format of "Xm".
    after_study_date (str): The time after the study date in the format of "Xm".

    Returns:
    Tuple[pd.DataFrame, int]: A tuple containing a dataframe and sim_cont.
    """
    try:
        pi.set_pi_page_config(pi.TagCount, 100, OperationTimeoutOverride=120)
        start_datetime, end_datetime, interval = _func_pi_dates(
            study_date, str(interval), before_study_date, after_study_date
        )
        print(start_datetime, " - ", end_datetime, " - ", interval)

        # Get interpolated data from PI
        df = pi.get_interpolated_data(
            pi_tags_list,
            datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S"),
            datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S"),
            interval=interval,
            chunk_num_days=70,
        )

        # Convert any non-numeric values to NaN and forward fill
        df = df.apply(pd.to_numeric, errors="coerce").ffill()

        # Check for NaN values in the data
        sim_cont = _check_data_for_nan(df)

        return df, sim_cont

    except Exception as exception:
        raise ValueError(
            f"Error in pull_pi_data, make sure : {exception}"
        ) from exception


# %%
# __main__
if __name__ == "__main__":
    # print(pi.search("WA.SWIS*MW*"))

    pi_tags_list = ["WA.SWIS.SUMM.WEMDE.NMWF"]
    study_date = "2022/12/31 2359"
    interval = "4s"
    before_study_date = "1h"
    after_study_date = "1h"
    df, sim_cont = pull_pi_data(
        pi_tags_list, study_date, interval, before_study_date, after_study_date
    )
    print(df)