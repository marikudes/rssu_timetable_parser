from typing import Any, cast

import requests

from .config import timeapiparams, timeapiurl


class DateParser:
    def response(self) -> dict[str, Any]:
        response = requests.get(timeapiurl, params=timeapiparams, timeout=10)
        return cast("dict[str, Any]", response.json())

    def get_current_year_month_day(self) -> str:
        data = self.response()
        return f"{data['year']}-{data['month']}-{data['day']}"


if __name__ == "__main__":
    print(DateParser().get_current_year_month_day())
