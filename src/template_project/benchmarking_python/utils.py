# ##
# Imports
# standar library imports
from typing import (
    Callable,
    Type,
    Union,
    TypeAlias,
)

# %%
# Type aliases

LoadersDictTypeHint: TypeAlias = dict[str, dict[str, dict[str, Union[Callable, Type]]]]