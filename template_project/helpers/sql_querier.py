# standard library imports
import logging
from typing import (
    Protocol,
    Any,
)
# third party imports
import pandas as pd
import cx_Oracle
import WA_db


def _initialise_oracle_client(oracle_client_path: str) -> None:
    """Initialise the Oracle client using the path to the Oracle client directory."""
    cx_Oracle.init_oracle_client(oracle_client_path)


def _get_sql_db_names() -> list[str]:
    """Get the names of the SQL databases from the WA_db module."""
    return list(WA_db.standard_dbs.keys())


def _connect_to_sql_databases(sql_db_names: list[str]) -> dict[str, Any]:
    """Connect to the SQL databases and return a dictionary of the connections."""
    sql_db_connection: dict[str, Any] = {}
    sql_db_name: str
    for sql_db_name in sql_db_names[0:2]:
        try:
            sql_db_connection[sql_db_name] = WA_db.connect(db_name=sql_db_name)
            logging.debug(f"Connected to {sql_db_name}")
        except cx_Oracle.DatabaseError:
            logging.warning(f"Could not connect to {sql_db_name}")
    return sql_db_connection


class SqlQuerier:

    def __init__(
        self,
        oracle_client_path: str = r"C:\Users\nbutterly\Oracle\instantclient_21_10",
    ) -> None:
        """Initialise the SqlQuerier class and store the arguments."""
        # store the arguments
        self._oracle_client_path: str = oracle_client_path

        # initialise the oracle client
        logging.info("Connecting to Oracle client...")
        _initialise_oracle_client(self._oracle_client_path)
        sql_db_to_connect: list[str] = _get_sql_db_names()
        self._sql_db_connections: dict[str, Any] = _connect_to_sql_databases(sql_db_to_connect)
        logging.info(f"Connected to {', '.join(list(self._sql_db_connections.keys()))}.")

    @property
    def sql_db_names(self) -> list[str]:
        """Return the names of the SQL databases available to query."""
        return list(self._sql_db_connections.keys())

    def query_to_pandas_dataframe(
        self,
        query: str,
        db_name: str = "WEMSDB",
    ) -> pd.DataFrame:
        """Return a pandas dataframe from a SQL query."""
        logging.info(f"Querying {db_name}...")
        df: pd.DataFrame = pd.read_sql(
            query,
            self._sql_db_connections[db_name].db
        )
        logging.info(f"Query fulfilled by {db_name}.")
        return df

    # # WIP: dask doesn't support SQL alchemy connections
    # def query_to_dask_dataframe(
    #     self,
    #     table_name: str,
    #     index_column: str = "id",
    #     db_name: str = "WEMSDB"
    # ) -> dd.DataFrame:
    #     """Return a dask dataframe from a SQL query."""
    #     return dd.read_sql_table(
    #         table_name=table_name,
    #         index_col=index_column,
    #         con=self._sql_db_connections[db_name].db,
    #     )


class QueryToPandasDataframCapable(Protocol):
    """Protocol interface for classes that can return a pandas dataframe from a SQL query."""
    def query_to_pandas_dataframe(
        self,
        query: str,
        db_name: str,
    ) -> pd.DataFrame:
        pass


# %%
# MAIN
if __name__ == "__main__":
    # set the sql query
    WEMSDB_query_1 = """SELECT
    f.facility_id,
    fc.short_name facility,
    pc.short_name participant,
    cr.effective_date facility_creation_date
FROM
    regn.facility_creation fc
    JOIN regn.facility f ON f.creation_id = fc.change_request_id
    JOIN regn.change_request cr ON cr.id = fc.change_request_id
    JOIN regn.participant p ON p.participant_id = fc.owner_id
    JOIN regn.participant_creation pc ON pc.change_request_id = p.creation_id
ORDER BY facility_creation_date
"""
    # set the sql database to connect to
    sql_querier: QueryToPandasDataframCapable = SqlQuerier()

    # get sql data and store in a dataframe
    pdf: pd.DataFrame = sql_querier.query_to_pandas_dataframe(
        query=WEMSDB_query_1,
        db_name="WEMSDB"
    )

    print()
    print("Pandas DataFrame")
    print()
    print(pdf.shape)
    print()
    print(pdf.head())
