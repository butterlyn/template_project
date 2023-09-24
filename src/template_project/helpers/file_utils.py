from typing import Iterable
from io import TextIOWrapper


def _find_index_containing_string(
    iterable_to_search: Iterable[str],
    string_to_locate: str,
) -> int:
    """
    Find the index of the first line in the list of lines that contains the given match string.

    Parameters
    ----------
    lines : List[str]
        A list of strings representing the lines in the file.
    match : str
        The string to search for in the lines.

    Returns
    -------
    int
        The index of the first line that contains the match string, or -1 if no line matches.

    """
    index: int
    iterable_entry: str
    for index, iterable_entry in enumerate(iterable_to_search):
        if string_to_locate in iterable_entry:
            return index
    return -1


def _replace_line_in_file(
    filename: str,
    line_index: int,
    replacement_line: str
) -> None:
    """
    Replace the line at a given line index in the given file with a new line.

    Parameters
    ----------
    filename : str
        The filename of a file in the current working directory, or a filepath.
    line_index : int
        The index of the line to replace.
    replacement_line : str
        The new string to replace the line with.

    Returns
    -------
    None

    """
    file: TextIOWrapper
    with open(filename, 'r') as file:
        file_content: list[str] = file.readlines()
        replacement_file_content = file_content.copy()
        replacement_file_content[line_index] = replacement_line
    with open(filename, 'w') as file:
        file.writelines(replacement_file_content)


def replace_file_line_containing_matching_string(
    filename: str,
    matching_string: str,
    replacement_line: str
) -> int:
    """
    Replace the first line in the file that contains the given match string
    with and replace the whole line with a replacement line.

    Parameters
    ----------
    filename : str
        The name of the file to modify in the current working directory, or a filepath.
    match : str
        The string to search for in the lines.
    replacement_line : str
        The new string to replace the line with.

    Returns
    -------
    int
        The index of the line that was replaced, or -1 if no line was replaced.

    """
    # read the file into a list of lines
    with open(filename, 'r') as file:
        lines: list[str] = file.readlines()

    # find the index of the first line that contains the match string
    line_index: int = _find_index_containing_string(lines, matching_string)

    # if matching string not found, return -1
    if line_index != -1:
        _replace_line_in_file(
            filename=filename,
            line_index=line_index,
            replacement_line=replacement_line,
        )
    return line_index  # return the index of the line that was replaced, or -1 if no line was replaced


def append_string_to_start_or_end_of_file(
    filepath: str,
    string_to_append: str,
    end_of_file: bool = False,
) -> None:
    """Append a string to the beginning or end of a file.

    Parameters
    ----------
    filepath : str
        The path of the file to append to.
    string_to_append : str
        The string to append to the file.
    end_of_file : bool, optional
        Whether to append the string to the beginning or end of the file.
        Defaults to beginning.

    Returns
    -------
    None
    """
    with open(filepath, 'r+') as f:
        contents = f.read()
        f.seek(0)
        if end_of_file:
            f.write(contents + '\n' + string_to_append)
        else:
            f.write(string_to_append + '\n' + contents)
