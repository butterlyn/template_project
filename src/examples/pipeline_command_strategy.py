from abc import ABC, abstractmethod
from typing import Any, List


class Command(ABC):
    """Abstract base class for commands"""

    @abstractmethod
    def execute(self, data: Any) -> Any:
        """Execute the command on the input data and return the output data"""
        pass


class FlattenDictCommand(Command):
    """Command to flatten a nested dictionary to a dictionary one level deep"""

    def __init__(self, parent_key: str = '', sep: str = '.'):
        self._parent_key = parent_key
        self._sep = sep

    def execute(self, data: dict) -> dict[str, Any]:
        """Flatten the dictionary"""
        items = []
        for key, value in data.items():
            new_key = self._parent_key + self._sep + key if self._parent_key else key
            if isinstance(value, dict):
                items.extend(FlattenDictCommand(new_key, sep=self._sep).execute(value).items())
            else:
                items.append((new_key, value))
        return dict(items)


class DictionaryDeepestKeyValuePairsCommand(Command):
    """Command to return the list of the deepest key-value pairs of a dictionary"""

    def __init__(self, max_level: int | None = None):
        self._max_level = max_level

    def execute(self, data: dict) -> list:
        """Return the list of the deepest key-value pairs of the dictionary"""
        if self._max_level is None:
            self._max_level = float("inf")

        result = []
        for key, value in data.items():
            (
                result.extend(DictionaryDeepestKeyValuePairsCommand(max_level=(self._max_level - 1)).execute(value))
                if isinstance(value, dict) and (self._max_level > 0)
                else result.append((key, value))
            )
        return result


class SortDictByValuesCommand(Command):
    """Command to sort a dictionary by its values"""

    def __init__(self, reverse: bool = False):
        self._reverse = reverse

    def execute(self, data: dict) -> dict:
        """Sort the dictionary by its values"""
        return dict(
            sorted(
                data.items(),
                key=lambda item: item[1],
                reverse=self._reverse
            )
        )


class DataPipeline:
    """A data pipeline that processes input data through a series of commands"""

    def __init__(self, commands: List[Command]):
        self._commands = commands

    def process_data(self, data: Any) -> Any:
        """Process the input data through the pipeline and return the output data"""
        for command in self._commands:
            data = command.execute(data)
        return data


# Demonstration
if __name__ == "__main__":
    # nested dict for example
    nested_dict: dict = {
        "a": {
            "b": {
                "c": 66,
                "d": 22,
            },
            "e": 33,
        },
        "f": 88,
    }

    # create commands
    flatten_command = FlattenDictCommand()
    deepest_command = DictionaryDeepestKeyValuePairsCommand()
    sort_command = SortDictByValuesCommand(reverse=True)

    # create data pipeline with commands
    pipeline = DataPipeline([flatten_command, deepest_command, sort_command])

    # process data through pipeline and print result
    result = pipeline.process_data(nested_dict)
    print(result)