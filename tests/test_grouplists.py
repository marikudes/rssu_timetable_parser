import json
from unittest.mock import AsyncMock

import aiohttp
import pytest

from src.app.parser.config import getgrouplisturl, headers
from src.app.parser.getgroupslist import GroupListParser


@pytest.mark.asyncio
async def test_group_list_parser_response() -> None:
    parser = GroupListParser()
    mock_session = AsyncMock(spec=aiohttp.ClientSession)
    mock_response = AsyncMock()

    mock_session.post.return_value.__aenter__.return_value = mock_response
    mock_response.text.return_value = json.dumps(
        {"suggestions": ["Группа 1А", "Группа 1Б", "Группа 2А"]}
    )

    result = await parser.response(mock_session)

    assert result == {"suggestions": ["Группа 1А", "Группа 1Б", "Группа 2А"]}
    mock_session.post.assert_called_once_with(getgrouplisturl, headers=headers, ssl=False)
