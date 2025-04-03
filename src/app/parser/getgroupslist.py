import json
from pathlib import Path
from typing import Any, cast

import requests

from .config import getgrouplisturl, headers


class GroupListParser:
    def response(self) -> dict[str, Any]:
        response = requests.post(getgrouplisturl, headers=headers, timeout=10, verify=False)
        return cast("dict[str, Any]", response.json())

    def save_data(self) -> None:
        json_path = Path(__file__).parent.parent / "data" / "groups.json"
        data = self.response()

        with json_path.open("w", encoding="utf-8") as file:
            suggestions = data["suggestions"]
            json.dump(suggestions, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    print(GroupListParser().response())
