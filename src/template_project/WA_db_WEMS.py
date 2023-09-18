# %%
# IMPORTS

import WA_db
import pandas as pd
import cx_Oracle

# %%
# GLOBAL VARIABLES

...


# %%
# Logger

...

# %%
# HELPER FUNCTIONS


def _initialise_oracle_client(oracle_client_path: str) -> None:
    # initialse oracle client
    cx_Oracle.init_oracle_client(oracle_client_path)


def _get_sql_db_names() -> list:
    return list(WA_db.standard_dbs.keys())


def _connect_to_sql_databases(sql_db_names: list) -> dict:
    sql_db_connection = {}
    for sql_db_name in sql_db_names[0:2]:
        try:
            sql_db_connection[sql_db_name] = WA_db.connect(db_name=sql_db_name)
        except cx_Oracle.DatabaseError as e:
            continue
    return sql_db_connection


# %%
# COMPOSABLE FUNCTIONS


def connect_to_sql_databases(
    oracle_client_path: str,
) -> dict:
    _initialise_oracle_client(oracle_client_path)
    sql_db_names = _get_sql_db_names()
    return _connect_to_sql_databases(sql_db_names)


# %%
# MODULE-LEVEL FUNCTION(S)


class SQLInfo:
    def __init__(
        self,
        oracle_client_path: str = r"C:\Users\nbutterly\Oracle\instantclient_21_10",
    ) -> None:
        self.oracle_client_path = oracle_client_path
        self.sql_db = connect_to_sql_databases(oracle_client_path)

    def get_sql_info(self, query: str, db_name: str = "WEMSDB") -> pd.DataFrame:
        sql_query_return = pd.read_sql(query, self.sql_db[db_name].db)
        return sql_query_return


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
    sql_info = SQLInfo()

    # get sql data and store in a dataframe
    df_sql_info = sql_info.get_sql_info(query=WEMSDB_query_1, db_name="WEMSDB")

    df_sql_info.shape

    print(df_sql_info.head())
