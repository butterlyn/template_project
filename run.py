import logging
import pandas as pd
from template_project.helpers import (
    SqlQuerier,
    # getRichLogger,
    # dictionary_deepest_key_value_pairs,
    # flatten_dict,
    # count_final_values_in_dict,
    # validate_arguments,
)


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

query_list: list[str] = [
    WEMSDB_query_1,
    WEMSDB_query_1,
]

# set the sql database to connect to
sql_querier: SqlQuerier = SqlQuerier()

# get sql data and store in a dataframe
query: str
pdf_list: list[pd.DataFrame] = []
for query in query_list:
    pdf_list += [
        sql_querier.query_to_pandas_dataframe(
            query=query,
            db_name="WEMSDB"
        )
    ]

logging.info("Printing dataframes...")
print()

pdf: pd.DataFrame
for pdf in pdf_list:
    print(pdf.head(10))
    print()
