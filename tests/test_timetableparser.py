from unittest.mock import Mock, patch

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


def test_response() -> None:
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response

        parser = TimeTableParser()
        result = parser.response("2025-04-03")

        assert result == mock_response_data
        mock_post.assert_called_once()


def test_parse_timetable() -> None:
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response

        parser = TimeTableParser()
        result = parser.parse_timetable("2025-04-03")

        expected_result = [
            {
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
        mock_post.assert_called_once()
