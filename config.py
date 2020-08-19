import json
import os
from copy import deepcopy
from typing import Any

defaults = {
    "library": "test_library",
    "telegram": {
        "enabled": False,
        "token": "",
        "users": []
    },
    "web": {
        "enabled": False,
        "port": 5000
    }
}


class Config:
    def __init__(self, cfg_path: str):
        self._data: dict = deepcopy(defaults)

        if os.path.exists(cfg_path):
            with open(cfg_path, "r") as config_file:
                self._data = json.loads(config_file.read())
                print("Using config file", config_file.name)
        else:
            print("Warning:", cfg_path, "not found, using defaults.")

    def get(self, path: str) -> Any:
        """ Example:
        cfg.get("telegram.enabled")

        Returns default value if key does not exist
        """
        u_obj: Any = self._data
        d_obj: Any = defaults
        for key in path.split("."):
            if key in u_obj:
                u_obj = u_obj[key]
                d_obj = d_obj[key]
            else:
                u_obj = d_obj[key]
                d_obj = u_obj[key]
        return u_obj
