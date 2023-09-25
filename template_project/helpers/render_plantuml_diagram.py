# %%
# IMPORTS
# standard library
import os
import logging
# third-party
from plantweb.render import render_file
# local imports
from . import (
    replace_file_line_containing_matching_string,
    append_string_to_start_or_end_of_file,
)

# %%
# CONSTANTS

_VALID_THEMES: frozenset[str] = frozenset(
    {
        "_none_",
        "amiga",
        "aws-orange",
        "black-knight",
        "bluegray",
        "blueprint",
        "carbon-gray",
        "cerulean",
        "cerulean-outline",
        "cloudscape-design",
        "crt-amber",
        "crt-green",
        "cyborg",
        "cyborg-outline",
        "hacker",
        "lightgray",
        "mars",
        "materia",
        "materia-outline",
        "metal",
        "mimeograph",
        "minty",
        "mono",
        "plain",
        "reddress-darkblue",
        "reddress-darkgreen",
        "reddress-darkorange",
        "reddress-darkred",
        "reddress-lightblue",
        "reddress-lightgreen",
        "reddress-lightorange",
        "reddress-lightred",
        "sandstone",
        "silver",
        "sketchy",
        "sketchy-outline",
        "spacelab",
        "spacelab-white",
        "superhero",
        "superhero-outline",
        "toy",
        "united",
        "vibrant",
    }
)

_DEFAULT_THEME: str = "_none_"

_VALID_DIAGRAM_FORMATS: frozenset[str] = frozenset(
    {
        "svg",
        "png",
    }
)

_REQUIRED_PLANTUML_DECLARATION_BY_FILE_EXTENSION: dict[str, dict[str, str]] = {
    "json": {
        "header": "@startjson\n",
        "footer": "\n@endjson",
    },
    "yaml": {
        "header": "@startyaml\n",
        "footer": "\n@endyaml",
    },
    "yml": {
        "header": "@startyaml\n",
        "footer": "\n@endyaml",
    },
    "md": {  # assumes the markdown file already has the @startuml and @enduml declarations
        "header": "",
        "footer": "",
    },
    "txt": {  # assumes the txt file already has the @startuml and @enduml declarations
        "header": "",
        "footer": "",
    },
}


# %%
# HELPER FUNCTIONS

def _render_plantuml_diagram(
    filepath: str,
    diagram_format: str,
    output_filepath: str,
    header: str,
    footer: str,
) -> str:
    """rendering the plantUML diagram and saving to file. Returns the path of the rendered diagram."""
    try:
        # make a temporary copy of the file
        temporary_filepath: str = filepath + ".tmp"
        with open(filepath, 'r') as f:
            with open(temporary_filepath, 'w') as f_copy:
                f_copy.write(f.read())
                logging.debug(f"temporary copy of file created at {temporary_filepath}")

        # append header and footer to the temporary file
        append_string_to_start_or_end_of_file(  # append the footer to the end of the file
            filepath=temporary_filepath,
            string_to_append=footer,
            end_of_file=True,
        )
        append_string_to_start_or_end_of_file(  # append the header to the beginning of the file
            filepath=temporary_filepath,
            string_to_append=header,
            end_of_file=False,
        )

        # render the diagram
        output_filepath_resolved: str = render_file(
            infile=temporary_filepath,
            renderopts={
                'engine': 'plantuml',
                'format': diagram_format,
            },
            outfile=output_filepath
        )
    finally:
        # delete the temporary file, even if there is an error
        os.remove(temporary_filepath)

    # return the path of the rendered diagram
    return output_filepath_resolved


def _get_required_plantuml_header_footer(
    filepath: str,
    input_file_extension: str,
    theme: str,
    _REQUIRED_PLANTUML_DECLARATION_BY_FILE_EXTENSION: dict[str, dict[str, str]],
) -> tuple[str, str]:
    """determining the header and footer required for the plantUML diagram to render
    if the theme is already specified in the file, replace the theme with the specified theme"""

    # get the required header and footer plantUML declaration corresponding to the file type
    header_required_plantuml_declaration: str = _REQUIRED_PLANTUML_DECLARATION_BY_FILE_EXTENSION[input_file_extension]["header"]
    footer_required_plantuml_declaration: str = _REQUIRED_PLANTUML_DECLARATION_BY_FILE_EXTENSION[input_file_extension]["footer"]
    logging.debug(f"header_required_plantuml_declaration: {header_required_plantuml_declaration}")
    logging.debug(f"footer_required_plantuml_declaration: {footer_required_plantuml_declaration}")

    # get the string required to set the theme in the plantUML diagram
    header_theme_declaration: str = f"!theme {theme}\n"

    # if plantuml markdown hint "```plantuml" is present in the file, remove it
    line_in_file_with_plantuml_markdown_hint: int = replace_file_line_containing_matching_string(
        filename=filepath,
        matching_string="```plantuml",
        replacement_line="",
    )
    logging.debug(f"plantuml markdown hint removed from file at line {line_in_file_with_plantuml_markdown_hint}")

    # if theme is already specified in the file, replace the theme with the specified theme
    line_in_file_already_specifying_theme: int = replace_file_line_containing_matching_string(
        filename=filepath,
        matching_string="!theme",
        replacement_line=header_theme_declaration,
    )
    theme_already_specified_in_file_and_was_replaced: bool = (
        True if line_in_file_already_specifying_theme != -1
        else False
    )
    logging.debug(f"Theme was already specified in file: {theme_already_specified_in_file_and_was_replaced}")
    logging.debug(f"Line in file specifying theme: {line_in_file_already_specifying_theme}. If -1, then theme was not specified in file.")

    # specify the header and footer for the plantUML diagram
    header: str = (
        header_required_plantuml_declaration if theme_already_specified_in_file_and_was_replaced
        else header_required_plantuml_declaration + header_theme_declaration
    )
    footer: str = footer_required_plantuml_declaration

    # return the header and footer
    return header, footer


# %%
# FUNCTIONS

def render_plantuml_diagram(
    filepath: str,
    diagram_format: str = 'svg',
    theme: str | None = None,
    output_filepath: str | None = None,
    _VALID_THEMES: frozenset[str] = _VALID_THEMES,
    _DEFAULT_THEME: str = _DEFAULT_THEME,
    _VALID_DIAGRAM_FORMATS: frozenset[str] = _VALID_DIAGRAM_FORMATS,
    _REQUIRED_PLANTUML_DECLARATION_BY_FILE_EXTENSION: dict[str, dict[str, str]] = _REQUIRED_PLANTUML_DECLARATION_BY_FILE_EXTENSION,
) -> str:
    """Render a file as a plantUML diagram and saves to svg or png. This includes json files, yaml files,
    or a markdown or text files containing any valid plantUML diagram syntax (without @umlstart @umlend).

    Parameters
    ----------
    filepath : str
        The path of the file to render. Must be a json, yaml, yml.
        Also, md or txt files are supported if they contain valid syntax for a plantUML diagram,
        but the theme will not be applied.
    file_format : str, optional
        Diagram render format. 'svg' or 'png'. Defaults to 'svg'.
    theme: str, optional
        Diagram theme. '_default_', 'blueprint'. Defaults to '_default_'.
        See https://the-lum.github.io/puml-themes-gallery/ for more options.
    output_filepath: str, optional
        The path to save the rendered diagram to. Defaults to the current working directory.

    Returns
    -------
    str
        The path of the rendered diagram file.
    """
    # ~~~~~ log constants ~~~~~ #

    logging.debug(f"valid themes: {_VALID_THEMES}")
    logging.debug(f"default theme: {_DEFAULT_THEME}")
    logging.debug(f"valid diagram formats: {_VALID_DIAGRAM_FORMATS}")
    logging.debug(f"plantUML header and footer declarations by file extension: {_REQUIRED_PLANTUML_DECLARATION_BY_FILE_EXTENSION}")

    # sanity check that the default theme is supported
    if _DEFAULT_THEME not in _VALID_THEMES:
        critical_error_message: str = f"Default theme {_DEFAULT_THEME} is not supported. Function is broken, seek help."
        logging.critical(critical_error_message)
        raise ValueError(f"Default theme {_DEFAULT_THEME} is not supported.")

    # ~~~~~ resolve unset inputs ~~~~~ #

    # if theme is not specified, use the default theme
    if theme is None:
        theme = _DEFAULT_THEME

    # if the output filepath is not specified, use the current working directory
    current_working_directory: str = os.getcwd()
    output_filepath_resolved: str = (
        os.path.join(current_working_directory, f"output_diagram.{diagram_format}") if output_filepath is None
        else output_filepath
    )

    # ~~~~~ validate inputs ~~~~~ #

    error_message: str = ""
    warning_message: str = ""

    # check if the inputted diagram theme is supported
    if theme not in _VALID_THEMES:
        theme = _DEFAULT_THEME
        warning_message = f"Theme {theme} is not supported, setting to default. Please use a valid theme from https://the-lum.github.io/puml-themes-gallery/."
        logging.warning(warning_message)

    # check if the input file exists
    if not os.path.isfile(filepath):
        error_message = f"File {filepath} does not exist."
        logging.error(error_message)
        raise FileNotFoundError(error_message)

    # check that the output filepath exists
    if not os.path.isdir(os.path.dirname(output_filepath_resolved)):
        error_message = f"Output filepath {output_filepath_resolved} does not exist."
        logging.error(error_message)
        raise ValueError(error_message)

    # check that the output filepath is a filepath and not a directory
    if os.path.isdir(output_filepath_resolved):
        warning_message = f"Output filepath {output_filepath_resolved} is a directory, not a filepath. Default filename 'output_diagram' will be used."
        logging.warning(warning_message)
        output_filepath_resolved = os.path.join(output_filepath_resolved, f"output_diagram.{diagram_format}")

    # check if the input file extension is supported
    input_file_extension: str = filepath.split(".")[-1]  # get the file extension
    valid_input_file_extensions: set[str] = set(_REQUIRED_PLANTUML_DECLARATION_BY_FILE_EXTENSION.keys())
    if input_file_extension not in valid_input_file_extensions:
        error_message = f"File type {input_file_extension} is not supported. Please use one of {valid_input_file_extensions}."
        logging.error(error_message)
        raise ValueError(error_message)

    # check if the diagram format is supported
    if diagram_format not in _VALID_DIAGRAM_FORMATS:
        error_message = f"Diagram format {diagram_format} is not supported. Please use svg or png."
        logging.error(error_message)
        raise ValueError(error_message)

    # ~~~~~ business logic ~~~~~ #

    # get the required header and footer plantUML declaration corresponding to the file type
    header: str
    footer: str
    header, footer = _get_required_plantuml_header_footer(
        filepath=filepath,
        input_file_extension=input_file_extension,
        theme=theme,
        _REQUIRED_PLANTUML_DECLARATION_BY_FILE_EXTENSION=_REQUIRED_PLANTUML_DECLARATION_BY_FILE_EXTENSION,
    )

    # render the plantUML diagram
    output_filepath_resolved = _render_plantuml_diagram(
        filepath=filepath,
        diagram_format=diagram_format,
        output_filepath=output_filepath_resolved,
        header=header,
        footer=footer,
    )
    logging.debug(f"output_filepath_resolved: {output_filepath_resolved}")

    # return the path of the rendered diagram
    return output_filepath_resolved


# %%
# EXAMPLE USAGE

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    filepath: str = "test.json"

    output_filepath: str = render_plantuml_diagram(
        filepath=filepath,
        diagram_format='svg',
        theme='materia',
        output_filepath=None,
    )

    print(output_filepath)

    # example svg output: https://tinyurl.com/5e5tzxm5
