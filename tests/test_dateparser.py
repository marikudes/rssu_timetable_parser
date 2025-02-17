from unittest.mock import Mock, patch

from parser.config import timeapiparams, timeapiurl
from parser.dateparser import DateParser

dayy = 17
monthh = 2
yearr = 2025


def test_response() -> None:
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {
            "day": dayy,
            "month": monthh,
            "year": yearr,
        }
        mock_get.return_value = mock_response

        parser = DateParser()
        result = parser.response()

        assert result == {"day": dayy, "month": monthh, "year": yearr}
        mock_get.assert_called_once_with(timeapiurl, params=timeapiparams, timeout=10)


def test_get_day_month_year() -> None:
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {
            "day": dayy,
            "month": monthh,
            "year": yearr,
        }
        mock_get.return_value = mock_response

        parser = DateParser()
        day, month, year = parser.get_current_day_month_year()

        assert day == dayy
        assert month == monthh
        assert year == yearr
        mock_get.assert_called_once_with(timeapiurl, params=timeapiparams, timeout=10)
