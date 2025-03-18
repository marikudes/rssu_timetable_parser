from unittest.mock import Mock, patch

from src.parser.config import timeapiparams, timeapiurl
from src.parser.date_parser import DateParser

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


def test_get_year_month_day() -> None:
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {
            "day": dayy,
            "month": monthh,
            "year": yearr,
        }
        mock_get.return_value = mock_response

        parser = DateParser()
        response = parser.get_current_year_month_day()

        assert response == f"{yearr}-{monthh}-{dayy}"
        mock_get.assert_called_once_with(timeapiurl, params=timeapiparams, timeout=10)
