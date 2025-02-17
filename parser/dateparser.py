from typing import Any, cast

import requests
from config import timeapiparams, timeapiurl


class DateParser:
    def response(self) -> dict[str, Any]:
        response = requests.get(timeapiurl, params=timeapiparams, timeout=10)
        return cast(dict[str, Any], response.json())

    def get_current_day_month_year(self) -> tuple[int, int, int]:
        data = self.response()
        return data["day"], data["month"], data["year"]
