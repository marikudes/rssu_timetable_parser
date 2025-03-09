from typing import Any, cast

import requests
from config import headers, timetableparams, timetableurl


class TimeTableParser:
    def response(self) -> dict[str, Any]:
        response = requests.post(
            timetableurl,
            headers=headers,
            data=timetableparams,
            timeout=10,
            verify=False,
        )

        return cast(dict[str, Any], response.json())
