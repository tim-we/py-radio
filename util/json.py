import json
import os
from typing import TypeVar, Any, Optional

T = TypeVar('T')


class JSONFile:
    def __init__(self, file: str = "", file_content: str = ""):
        self._data: dict = {}
        self.file: Optional[str] = None

        json_string = ""

        if file_content == "":
            assert file != ""
            if os.path.exists(file):
                with open(file, "r") as json_file:
                    json_string = json_file.read()
                    self.file = file
            else:
                print("Warning:", file, "not found.")
        else:
            json_string = file_content

        if not json_string == "":
            self._data = json.loads(json_string)

    def get(self, path: str, default: T, fail: bool = False, expected_type: Optional[Any] = None) -> T:
        """ Example:
        cfg.get("telegram.enabled")

        Returns default value if key does not exist
        """
        obj: Any = self._data
        for key in path.split("."):
            if key in obj:
                obj = obj[key]
            else:
                if fail:
                    raise ValueError("{} does not contain '{}'".format(self.file or "JSON", path))
                else:
                    return default
        if expected_type is not None:
            if not isinstance(obj, expected_type):
                raise TypeError("{} does not match the expected type {}.".format(path, expected_type))
        return obj
