# standard
import re
from typing import (
    TypedDict,
    MutableMapping,
    cast,
)
from typing_extensions import (
    NotRequired,
)
from pathlib import Path
import json
import logging
# third party
import docx
from docx.text.paragraph import Paragraph
from docx.document import Document
import polars as pl
from rich.progress import Progress
# local
from helpers.rich_logger import getRichLogger

logger: logging.Logger = getRichLogger(
    logging_level="INFO",
    logger_name=__name__,
    traceback_show_locals=True,
    traceback_extra_lines=10,
    traceback_suppressed_modules=(),
)

# logging.basicConfig()
# logger: logging.Logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)


class WemRulesClauseDict(TypedDict):
    """
    A dictionary representing a clause or sub-clause in the WEM Rules.

    Attributes:
        level (NotRequired[str]): The level of the clause, as indicated
            by the style name in the WEM Rules Word Document.
        identifier (str): The index (e.g. "1.5.3.", "1.7.") or sub-clause
            index (e.g., "(a)", "ii.").
        content (str): The text content of the clause.
        wem_rules_publication_iso_date (str): The date of publication
            of the version of the WEM Rules from which the clause is
            extracted. YYYY-MM-DD ISO date format.
        position_in_document (NotRequired[int]): The paragraph position
            index of the clause in the WEM Rules Word Document.
        style_name (NotRequired[str]): The style name of the clause in
            the WEM Rules Word Document. Used to derive the level of
            the clause.
    """
    level: NotRequired[int]
    identifier: str
    parent_identifier: NotRequired[str]
    content: str
    position_in_document: int
    wem_rules_publication_iso_date: str
    style_name: NotRequired[str]


def _extract_possible_clauses(
    docx_filepath: str,
    wem_rules_publication_iso_date: str,
) -> list[WemRulesClauseDict]:
    """
    Extracts all Word document paragraphs and stores as a list of
    dictionaries.
    """

    # create an empty dictionary to store the possible clauses
    possible_clauses: list[WemRulesClauseDict] = list()
    logger.debug(f"Empty dictionary initialised: {possible_clauses=}")

    # open the Word document
    doc: Document = docx.Document(docx_filepath)

    # read in all the paragraphs in the Word document and their styles
    paragraph: Paragraph
    paragraph_index: int
    for paragraph_index, paragraph in enumerate(doc.paragraphs):
        style_name: str = paragraph.style.name
        paragraph_content: str = paragraph.text

        # if the paragraph is heading, then store it as a possible clause
        match: re.Match | None = re.match(
            r"^(.*?)\t(.*)$",
            paragraph_content
        )
        if match:
            possible_clause_identifier: str = match.group(1)
            possible_clause_content: str = match.group(2)
            posible_clause: WemRulesClauseDict = {
                "identifier": possible_clause_identifier,
                "content": possible_clause_content,
                "position_in_document": paragraph_index,
                "wem_rules_publication_iso_date": wem_rules_publication_iso_date,
                "style_name": style_name,
            }
            logger.debug(f"{posible_clause=}")
            possible_clauses.append(posible_clause)

    return possible_clauses


def _map_clause_style_to_level(
    possible_clauses: list[WemRulesClauseDict],
    style_to_clause_level_mapping: dict[str, int],
) -> list[WemRulesClauseDict]:
    """
    Filters the possible clauses to only include clauses in the WEM Rules
    according to a list of valid Word document styles.
    """
    # create an empty list to store the filtered clauses
    valid_clauses: list[WemRulesClauseDict] = list()
    logger.debug(f"Empty list initialised: {valid_clauses=}")

    # iterate through the possible clauses
    possible_clause: WemRulesClauseDict
    valid_clause: WemRulesClauseDict
    for possible_clause in possible_clauses:
        if possible_clause["style_name"] in style_to_clause_level_mapping:
            # add the possible clause to the list of filtered clauses
            valid_clause = possible_clause
            logger.debug(f"{valid_clause=}")
            # replace the style name key with the clause level key
            valid_clause["level"] = \
                style_to_clause_level_mapping[valid_clause["style_name"]]
            # delete the style name key
            del valid_clause["style_name"]
            # add the filtered clause to the list of filtered clauses
            valid_clauses.append(valid_clause)

    return valid_clauses


def _save_list_of_dicts_to_ndjson(
    list_of_dicts: list[MutableMapping],
    save_filepath: str
) -> None:
    """Converts a list of dictionaries to a NDJSON file."""
    with open(save_filepath, "w", encoding='utf-8') as file:
        for dictionary in list_of_dicts:
            json.dump(dictionary, file)
            file.write("\n")


def _correct_subclause_identifiers(
    valid_clauses: list[WemRulesClauseDict],
    levels_corresponding_to_subclauses: list[int],
) -> list[WemRulesClauseDict]:
    """
    Corrects the sub-clause identifiers in the list of valid clauses.
    E.g., (ii) to 7.13.1EA(c)(ii)
    """

    ...

    logger.error(NotImplementedError)

    valid_clauses_corrected_subclause_identifiers: list[WemRulesClauseDict] = \
        valid_clauses

    return valid_clauses_corrected_subclause_identifiers


def _create_markdown_file(
    wem_rules_clause: WemRulesClauseDict,
    save_directory: str
) -> None:
    """Creates a markdown file for a WEM Rules clause."""
    clause_save_filepath: Path = Path(
        save_directory,
        (
            f"{str(wem_rules_clause['position_in_document'])}"
            "_"
            f"{wem_rules_clause['identifier']}"
            ".md"
        )
    )

    # create parent directories for the filepath if they don't exist
    clause_save_filepath.parent.mkdir(parents=True, exist_ok=True)

    # create the markdown file with wem rules contents
    with clause_save_filepath.open("w", encoding='utf-8') as file:
        # write the clause content to the markdown file
        file.write(wem_rules_clause["content"])


def wem_rules_ndjson_to_mkdown_files(
    filepath: str,
    save_directory: str,
    progress_bar: bool = True,
) -> pl.DataFrame:
    """
    Converts a NDJSON file of WEM Rules clauses to a series
    of markdown files.
    """

    # load the newline-delimited JSON file of WEM Rules clauses
    df_wem_rules_clauses: pl.DataFrame = (
        pl.read_ndjson(filepath)
    )

    wem_rules_clause: WemRulesClauseDict
    if progress_bar:
        # create a progress bar
        with Progress() as progress:
            progress_bar_description: str = (
                "[cyan]WEM rules ndjson to markdown..."
            )
            task = progress.add_task(
                description=progress_bar_description,
                total=len(df_wem_rules_clauses)
            )

            # convert the NDJSON file of WEM Rules clauses to markdown files
            for wem_rules_clause in df_wem_rules_clauses.iter_rows(named=True):
                _create_markdown_file(wem_rules_clause, save_directory)

                # update the progress bar
                progress.update(
                    task_id=task,
                    advance=1,
                )
                progress.update(
                    task_id=task,
                    description=" ".join(
                        [
                            progress_bar_description,
                            (
                                f"({progress.tasks[0].completed}"
                                "/"
                                f"{progress.tasks[0].total})"
                            )
                        ]
                    ),
                )
    else:
        # convert the NDJSON file of WEM Rules clauses to markdown files
        for wem_rules_clause in df_wem_rules_clauses.iter_rows(named=True):
            _create_markdown_file(wem_rules_clause, save_directory)

    return df_wem_rules_clauses


class ExtractWemRulesClausesKwargs(TypedDict):
    """Keyword arguments for the extract_wem_rules_clauses function."""
    docx_filepath: str
    wem_rules_publication_iso_date: str
    style_to_clause_level_mapping: dict[str, int]
    levels_corresponding_to_subclauses: list[int]
    save_filepath: NotRequired[str]
    progress_bar: NotRequired[bool]


def extract_wem_rules_clauses(
    docx_filepath: str,
    wem_rules_publication_iso_date: str,
    style_to_clause_level_mapping: dict[str, int],
    levels_corresponding_to_subclauses: list[int],
    save_filepath: str | None = None,
    progress_bar: bool = True,
) -> None:
    """
    Extracts all possible clauses from the WEM Rules Word document and
    stores them as a newline-delimited JSON file.
    """
    # extract all possible clauses from the WEM Rules Word document
    logger.info("Extracting possible clauses...")
    possible_clauses: list[WemRulesClauseDict] = _extract_possible_clauses(
        docx_filepath=docx_filepath,
        wem_rules_publication_iso_date=wem_rules_publication_iso_date,
    )

    # add the clause level to each clause based on the style name
    logger.info("Identifying valid clauses...")
    valid_clauses: list[WemRulesClauseDict] = _map_clause_style_to_level(
        possible_clauses=possible_clauses,
        style_to_clause_level_mapping=style_to_clause_level_mapping,
    )

    logger.info("Correcting subclause identifiers...")
    # correct the subclause identifiers
    valid_clauses_corrected_subclause_identifiers: list[WemRulesClauseDict] = \
        _correct_subclause_identifiers(
            valid_clauses,
            levels_corresponding_to_subclauses,
    )

    # correct subclause identifiers to include parent clause
    wem_rules_clauses: list[WemRulesClauseDict] = (
        valid_clauses_corrected_subclause_identifiers)

    # save the list of clauses to a newline-delimited JSON file
    if save_filepath is not None:
        # cast for static typecheckers, no impact at on runtime
        save_filepath = cast(str, save_filepath)

        logger.info(f"Saving clauses to {save_filepath}...")
        _save_list_of_dicts_to_ndjson(
            list_of_dicts=wem_rules_clauses,
            save_filepath=save_filepath,
        )

        logger.info("Converting WEM Rules clauses to markdown files...")
        df_wem_rules_clauses: pl.DataFrame = wem_rules_ndjson_to_mkdown_files(
            filepath=save_filepath,
            save_directory=(
                Path(save_filepath).parent / "markdown"
            ).resolve().__str__(),
            progress_bar=progress_bar,
        )
    else:
        logger.warning(
            "No savepath provided, skipping saving of WEM Rules clauses"
        )

    logger.info("WEM Rules clauses extraction complete.")


def test_extract_wem_rules_clauses(
    **kwargs: ExtractWemRulesClausesKwargs | None
) -> None:
    """Test the extract_wem_rules_clauses function."""

    # define default keyword arguments if not provided
    default_kwargs: ExtractWemRulesClausesKwargs = ExtractWemRulesClausesKwargs(
        docx_filepath=Path(
            "template_project",
            "wholesale_electricity_market_rules_-_1_october_2023.docx",
        ).resolve().__str__(),
        wem_rules_publication_iso_date="2023-10-01",
        style_to_clause_level_mapping={
            "MR Level 1": 1,
            "MR Level 2": 2,
            "MR Level 3": 3,
            "MR Level 4": 4,
            "MR Level 5": 5,
        },
        levels_corresponding_to_subclauses=[4, 5],
        save_filepath=r"template_project\wem_rules_clauses.ndjson",
        progress_bar=True,
    )

    # override any default keyword arguments with any provided
    if kwargs is not None:
        merged_default_provided_kwargs: ExtractWemRulesClausesKwargs = \
            default_kwargs
        merged_default_provided_kwargs.update(kwargs)

    extract_wem_rules_clauses(
        **merged_default_provided_kwargs,
    )


if __name__ == "__main__":
    test_extract_wem_rules_clauses()
