# %%
# IMPORTS
# standard libary imports
from typing import (
    Callable,
    Protocol,
)
import logging
# third party imports
from pydantic import (
    dataclasses,
    # DataclassTypeError,
    BaseModel,
    Field,
    validator,
    ValidationError,
    root_validator,
    validate_arguments,
    validate_model,
    # ConfigDict,
)
# local imports
from utils import LoadersDictTypeHint

# %%
# PROTOCOLS


# %%
# CLASSES

