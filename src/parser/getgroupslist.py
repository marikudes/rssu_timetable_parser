from typing import Any, cast

import requests
from config import getgrouplisturl, headers


class GroupListParser:
    def response(self) -> dict[str, Any]:
        response = requests.post(getgrouplisturl, headers=headers, timeout=10, verify=False)
        return cast("dict[str, Any]", response.json())


if __name__ == "__main__":
    print(GroupListParser().response())
