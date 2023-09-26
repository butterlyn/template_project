from docxcompose.composer import Composer
from docx import Document as Document_compose
from pathlib import Path
import logging
from typing import List, Optional, Union
import os

logging.basicConfig(level=logging.INFO) # Set the logging level to INFO or DEBUG
logger = logging.getLogger(__name__)

main_path = str(Path(r"C:\Users\nbutterly\OneDrive - Australian Energy Market Operator\Documents - WA Future System Design\1. Projects\221003-WA-Roadmap\02 - Working Files\03 WA Roadmap Report Writing\Sections").resolve())
regex_filter = "*.docx*"


def combine_all_docx(filename_master, files_list):
    number_of_sections = len(files_list)
    master = Document_compose(filename_master)
    composer = Composer(master)
    for i in range(0, number_of_sections):
        doc_temp = Document_compose(files_list[i])
        composer.append(doc_temp)
    composer.save("000_WA_Roadmap_MASTER.docx")


def get_filepaths_matching_regex(directory_path: str, regex_filter: str) -> List[str]:
    """
    Returns a list of filepaths in the specified directory and its subdirectories that match the specified regex pattern.

    Args:
        directory_path (str): The path to the directory to search for files.
        regex_filter (str): The regex pattern to match against file names.

    Returns:
        List[str]: A list of filepaths that match the specified regex pattern.

    Raises:
        ValueError: If the specified directory does not exist.

    Example:
        >>> get_filepaths_matching_regex("/path/to/directory", "*.txt")
        ['/path/to/directory/file1.txt', '/path/to/directory/subdir/file2.txt']
    """
    # Check if the specified directory exists
    if not Path(directory_path).is_dir():
        raise ValueError(f"Directory does not exist: {directory_path}")

    # Get a list of filepaths that match the specified regex pattern
    filepaths = [str(path) for path in Path(directory_path).glob(f"{regex_filter}")]

    # Log the number of files found and their names
    logger.info(
        f"Found {len(filepaths)} files matching {regex_filter} in {directory_path}"
    )
    for filepath in filepaths:
        logger.debug(f"{Path(filepath).relative_to(directory_path)}")

    # Return the list of filepaths
    return filepaths


def main() -> None:
    files_list = get_filepaths_matching_regex(main_path, regex_filter)
    filename_master = get_filepaths_matching_regex(main_path, "*010_WA_Roadmap_main.docx")[0]

    os.chdir(main_path)

    combine_all_docx(filename_master, files_list)


if __name__ == "__main__":
    main()
