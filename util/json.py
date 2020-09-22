import json
import os
from typing import Any, Optional


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

    def get_or_default(self, path: str, default: Any, value_type: type) -> Any:
        """ Example:
        cfg.get_or_default("telegram.enabled")

        Returns default value if key does not exist
        """
        assert isinstance(default, value_type)
        obj: Any = self._data
        for key in path.split("."):
            if key in obj:
                obj = obj[key]
            else:
                return default
        if not isinstance(obj, value_type):
            raise TypeError("{} does not match the expected type {}.".format(path, value_type))
        return obj

    def get_or_fail(self, path: str, value_type: type) -> Any:
        """ Example:
        cfg.get_or_default("telegram.enabled")

        Raises an exception if key does not exist
        """
        obj: Any = self._data
        for key in path.split("."):
            if key in obj:
                obj = obj[key]
            else:
                raise ValueError("{} does not contain '{}'".format(self.file or "JSON", path))
        if not isinstance(obj, value_type):
            raise TypeError("{} does not match the expected type {}.".format(path, value_type))
        return obj
