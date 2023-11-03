# %%
# IMPORTS
# standard
from alive_progress import alive_bar
import logging
from pathlib import Path
from io import TextIOWrapper
# third-party
from pyxlsb import (
    open_workbook,
    Workbook,
    Worksheet,
)
# local


# %%
# CONFIGURATION

MAIN_DIRECTORY: str = r"D:\NickB\repos\PDS_MDT_calculator\data"

PIPELINE_LAYERS: tuple[str, ...] = (
    "Raw",
    "Intermediate",
    "Primary",
    "Feature",
    "Model_inputs",
    "Models",
    "Model_outputs",
    "Reporting"
)

PIPELINE_LAYER_RELATIVE_DIRECTORIES: tuple[str, ...] = (
    "01_Input",
    "02_Processing/01_Intermediate",
    "02_Processing/02_Primary",
    "02_Processing/03_Feature",
    "02_Processing/04_Model_inputs",
    "02_Processing/05_Models",
    "02_Processing/06_Model_outputs",
    "03_Output",
)

PIPELINE_RAW_FILES: dict[str, str] = {
    "POE10_Low": "Interval demand data - 2023-24 to 2032-33 - POE10 - Low.xlsb",
    "POE10_Expected": "Interval demand data - 2023-24 to 2032-33 - POE10 - Expected.xlsb",
    "POE10_High": "Interval demand data - 2023-24 to 2032-33 - POE10 - High.xlsb",
}

# %%
# PARAMETERS

# None will proces all pipelines
# Options: None, "POE10 - Low", "POE10 - Expected", "POE10 - High"
PIPELINES_SELECTED: str | list[str] | None = None


# %%
# VALIDATE CONFIGURATION

...


# %%
# DERIVED CONFIGURATON & RESOLVE CONFIGURATION

def resolve_configuration_and_parameters() -> list[str]:
    logging.debug(f"Pipelines selected: {PIPELINES_SELECTED}")
    pipelines: tuple[str, ...] = tuple(PIPELINE_RAW_FILES.keys())
    logging.debug(f"Pipelines: {pipelines}")
    pipelines_to_process: list[str] = (
        list(pipelines)
        if PIPELINES_SELECTED is None
        else PIPELINES_SELECTED if isinstance(PIPELINES_SELECTED, list)
        else [PIPELINES_SELECTED]
    )
    logging.debug(f"Pipelines to process: {pipelines_to_process}")
    return pipelines_to_process


PIPELINE_TO_PROCESS: list[str] = resolve_configuration_and_parameters()


# %%
# FUNCTIONS

def get_pipeline_layer_directories(
    main_directory: str,
    pipeline_layers: tuple[str, ...],
    pipeline_layer_relative_directories: tuple[str, ...]
) -> dict[str, str]:
    """Get a dictionary of pipeline layer names and their absolute paths."""""

    pipeline_layer_absolute_directories_paths: list[Path] = [
        (Path(main_directory) / Path(pipeline_layer_relative_directory)).resolve()
        for pipeline_layer_relative_directory
        in pipeline_layer_relative_directories
    ]
    logging.debug(
        f"pipeline_layer_absolute_directories_paths: {pipeline_layer_absolute_directories_paths}")

    pipeline_layer_absolute_directories: list[str] = [
        str(pipeline_layer_absolute_directories_path)
        for pipeline_layer_absolute_directories_path
        in pipeline_layer_absolute_directories_paths
    ]
    logging.debug(
        f"pipeline_layer_absolute_directories: {pipeline_layer_absolute_directories}")

    pipeline_layer_directories_dictionary: dict[str, str] = dict(
        zip(
            pipeline_layers,
            pipeline_layer_absolute_directories,
        )
    )
    logging.debug(
        f"pipeline_layer_directories_dictionary: {pipeline_layer_directories_dictionary}")

    return pipeline_layer_directories_dictionary


def get_excel_file_filepath(
    pipeline_layer_directory: str,
    pipeline_raw_files: dict[str, str],
    current_pipeline: str,
) -> str:
    """Get the filepath of the raw data Excel file for the current pipeline."""
    excel_file_filepath: str = str(
        (
            Path(pipeline_layer_directory) /
            Path(current_pipeline) /
            pipeline_raw_files[current_pipeline]
        ).resolve()
    )
    logging.debug(f"excel_file_filepath for {current_pipeline}: {excel_file_filepath}")
    return excel_file_filepath


def get_csv_save_directory(
    pipeline_layer_directory: str,
    current_pipeline: str,
) -> str:
    """Get the directory path to save the CSV files to."""
    csv_save_directory: str = str(
        (
            Path(pipeline_layer_directory) /
            Path(current_pipeline)
        ).resolve()
    )
    logging.debug(f"csv_save_directory for {current_pipeline}: {csv_save_directory}")
    return csv_save_directory


# TODO: refactor this to use pandas read_excel
def split_xlxb_excel_tabs_to_csv(
    excel_file_filepath: str,
    csv_save_directory: str,
) -> list[str]:
    """
    Converts an xlxb Excel file with multiple sheets into multiple CSV files,
    with each CSV named after the corresponding Excel sheet. Returns a list
    of the CSV filepaths.
    """
    csv_save_filepaths: list[str] = []
    wb: Workbook
    with open_workbook(excel_file_filepath) as wb:
        sheets_names: list[str] = wb.sheets
        sheet_name: str
        with alive_bar(len(sheets_names), title=f"Processing sheets in Excel '{Path(excel_file_filepath).name}'") as bar:
            for sheet_name in sheets_names:
                sheet: Worksheet
                with wb.get_sheet(sheet_name) as sheet:
                    csv_save_filepath: str = f"{csv_save_directory}/{sheet_name}.csv"
                    csv_save_filepaths.append(csv_save_filepath)
                    csv_file: TextIOWrapper
                    with open(csv_save_filepath, "a") as csv_file:
                        for row in sheet.rows():
                            # retrieving content, too bespoke to typehint
                            values = [r.v for r in row]
                            csv_line = ",".join(
                                str(v) if v is not None else "" for v in values)
                            csv_file.write(csv_line + "\n")
                        bar()
    logging.debug(f"Sheets processed: {sheets_names}")
    return csv_save_filepaths


# %%
# PROCESS FUNCTIONS

def pipeline_split_xlxb_excel_tabs_to_csv(pipelines_to_process) -> list[str]:
    """Raw -> Intermediate pipeline layer"""

    INPUT_DATA_LAYER: str = "Raw"
    OUTPUT_DATA_LAYER: str = "Intermediate"

    for current_pipeline in pipelines_to_process:
        logging.info(
            f"Processing pipeline {current_pipeline}: Raw -> Intermediate...")

        logging.info("Getting pipeline layer directories...")
        pipeline_layer_directories_dictionary: dict[str, str] = get_pipeline_layer_directories(
            main_directory=MAIN_DIRECTORY,
            pipeline_layers=PIPELINE_LAYERS,
            pipeline_layer_relative_directories=PIPELINE_LAYER_RELATIVE_DIRECTORIES,
        )
        logging.info("Getting pipeline layer directories...DONE")

        logging.info("Getting Excel file filepath...")
        excel_file_filepath: str = get_excel_file_filepath(
            pipeline_layer_directory=pipeline_layer_directories_dictionary[INPUT_DATA_LAYER],
            pipeline_raw_files=PIPELINE_RAW_FILES,
            current_pipeline=current_pipeline,
        )
        logging.info("Getting Excel file filepath...DONE")

        logging.info("Getting CSV save directory...")
        csv_save_directory: str = get_csv_save_directory(
            pipeline_layer_directory=pipeline_layer_directories_dictionary[OUTPUT_DATA_LAYER],
            current_pipeline=current_pipeline,
        )
        logging.info("Getting CSV save directory...DONE")

        logging.info("Splitting xlxb Excel file tabs to CSV files...")
        csv_save_filepaths: list[str] = split_xlxb_excel_tabs_to_csv(
            excel_file_filepath=excel_file_filepath,
            csv_save_directory=csv_save_directory,
        )
        logging.info("Splitting xlxb Excel file tabs to CSV files...DONE")

        logging.info(
            f"Processing pipeline {current_pipeline}: Raw -> Intermediate...DONE")

    return csv_save_filepaths


# %%
# MAIN PROGRAM

def main() -> list[str]:
    """Main program, execute pipelines"""

    csv_save_filepaths: list[str] = pipeline_split_xlxb_excel_tabs_to_csv(pipelines_to_process=PIPELINE_TO_PROCESS)

    return csv_save_filepaths

    # # TODO: Deleted me after testing
    # csv_filepaths: list[str] = [
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/Raw data from AEMO (20230403).csv",
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/Notes.csv",
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/PV_Gen_Actual_Gen_EXP.csv",
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/Expected_POE10_FSC.csv",
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/Expected_POE10_Baseload.csv",
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/Expected_POE10_EV_Static.csv",
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/Expected_POE10_EV_VPP.csv",
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/Expected_POE10_Electrification.csv",
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/Expected_POE10_Hydrogen.csv",
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/Expected_POE10_PVNSG.csv",
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/Expected_POE10_BTM_Storage.csv",
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/BTM_Storage_VPP_Gen.csv",
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/BTM_Storage_VPP_Pump.csv",
    #     "/mnt/c/Users/nbutterly/OneDrive - Australian Energy Market Operator/Documents - WA Future System Design/7. Software/Minimum_demand_threshold_calculator/Input/CSV - 2023-24 to 2032033 - POE10 - Expected/Expected_POE10_PV_GEN.csv",
    # ]

    # # TODO: Move me to a function
    # logging.debug("Getting CSV file names...")
    # filepath_dictionary: dict[str, str] = _filepaths_list_to_dictionary(
    #     filepaths_list=csv_filepaths
    # )
    # logging.debug("Getting CSV file names...DONE")

    # # TODO: Deleted me after testing
    # selected_file: str = "BTM_Storage_VPP_Gen"
    # # Notes
    # # PV_Gen_Actual_Gen_EXP
    # # Expected_POE10_FSC
    # # Expected_POE10_Baseload
    # # Expected_POE10_EV_Static
    # # Expected_POE10_EV_VPP
    # # Expected_POE10_Electrification
    # # Expected_POE10_Hydrogen
    # # Expected_POE10_PVNSG
    # # Expected_POE10_BTM_Storage
    # # BTM_Storage_VPP_Gen
    # # BTM_Storage_VPP_Pump
    # # Expected_POE10_PV_GEN
    # selected_file_filepath: str = filepath_dictionary[selected_file]

    # df_traces: pd.DataFrame = pd.read_csv(
    #     selected_file_filepath,
    #     skiprows=[0, 2, 3, 4, 5],
    #     header=0,
    #     # engine="pyarrow",  # c, python, pyarrow, fastparquet
    # )
    # print(df_traces.debug())
    # print(df_traces.describe())
    # print(df_traces.head())
    # print(df_traces.columns)


if __name__ == "__main__":

    main()
