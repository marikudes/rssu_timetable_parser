import json
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from src.app.parser.config import headers, timetableparams, timetableurl
from src.app.parser.timetableparser import TimeTableParser

mock_response_data = {
    "html": """
    <div class="n-timetable-day__item">
        <span class="n-timetable-day__from">08:00</span>
        <span class="n-timetable-day__to">09:30</span>
        <article class="n-timetable-card">
            <h3 class="n-timetable-card__title">Математика</h3>
            <div class="n-timetable-card__category">Лекция</div>
            <div class="n-timetable-card__affiliation">Иванов И.И.</div>
            <div class="n-timetable-card__geo">
                <div class="n-timetable-card__affiliation">Корпус A</div>
                <div class="n-timetable-card__address">ул. Ленина, 10</div>
            </div>
            <div class="n-timetable-card__auditorium">Ауд. 101</div>
        </article>
    </div>
    """
}


@pytest.mark.asyncio
async def test_response() -> None:
    parser = TimeTableParser()
    mock_session = AsyncMock(spec=aiohttp.ClientSession)
    mock_response = AsyncMock()

    async def text_coroutine() -> str:
        return json.dumps(mock_response_data)

    mock_session.post.return_value.__aenter__.return_value = mock_response
    mock_response.text = text_coroutine

    result = await parser.response(mock_session, "2025-04-03", "GROUP-123")

    assert result == mock_response_data
    mock_session.post.assert_called_once_with(
        timetableurl,
        headers=headers,
        data={**timetableparams, "date": "2025-04-03", "group": "GROUP-123"},
        ssl=False,
    )


@pytest.mark.asyncio
async def test_parse_timetable() -> None:
    parser = TimeTableParser()
    mock_session = AsyncMock(spec=aiohttp.ClientSession)

    with patch.object(parser, "response", return_value=mock_response_data) as mock_response_method:
        result = await parser.parse_timetable(mock_session, "2025-04-03", "GROUP-123")

        expected_result = [
            {
                "date": "2025-04-03",
                "time": "08:00 - 09:30",
                "subject": "Математика",
                "category": "Лекция",
                "teacher": "Иванов И.И.",
                "building": "Корпус A",
                "address": "ул. Ленина, 10",
                "auditorium": "Ауд. 101",
            }
        ]

        assert result == expected_result
        mock_response_method.assert_called_once_with(mock_session, "2025-04-03", "GROUP-123")
