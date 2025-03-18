from unittest.mock import Mock, patch

from src.parser.config import getgrouplisturl, headers
from src.parser.getgroupslist import GroupListParser


def test_group_list_parser_response() -> None:
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {"groups": ["Группа 1А", "Группа 1Б", "Группа 2А"]}
        mock_post.return_value = mock_response

        parser = GroupListParser()
        result = parser.response()

        assert result == {"groups": ["Группа 1А", "Группа 1Б", "Группа 2А"]}
        mock_post.assert_called_once_with(
            getgrouplisturl, headers=headers, timeout=10, verify=False
        )
