import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

import requests
from bs4 import BeautifulSoup

from .config import headers, timetableparams, timetableurl


class TimeTableParser:
    def response(self, date: str, group: str) -> dict[str, Any]:
        params = timetableparams.copy()
        params["date"] = date
        params["group"] = group
        response = requests.post(
            timetableurl,
            headers=headers,
            data=params,
            timeout=10,
            verify=False,
        )
        return cast("dict[str, Any]", response.json())

    def parse_timetable(self, date: str, group: str) -> list[dict[str, str]]:
        data = self.response(date, group)
        html_content = data.get("html", "")
        soup = BeautifulSoup(html_content, "html.parser")

        timetable_items = []
        for item in soup.find_all("div", class_="n-timetable-day__item"):
            time_from = item.find("span", class_="n-timetable-day__from").text.strip()
            time_to = item.find("span", class_="n-timetable-day__to").text.strip()
            time = f"{time_from} - {time_to}"

            card = item.find("article", class_="n-timetable-card")
            subject = card.find("h3", class_="n-timetable-card__title").text.strip()
            category = card.find("div", class_="n-timetable-card__category").text.strip()

            affiliation_divs = card.find_all("div", class_="n-timetable-card__affiliation")
            teacher = affiliation_divs[0].text.strip() if affiliation_divs else ""

            geo = card.find("div", class_="n-timetable-card__geo")
            building = (
                geo.find("div", class_="n-timetable-card__affiliation").text.strip()
                if geo and geo.find("div", class_="n-timetable-card__affiliation")
                else ""
            )
            address = (
                geo.find("div", class_="n-timetable-card__address").text.strip()
                if geo and geo.find("div", class_="n-timetable-card__address")
                else ""
            )

            auditorium = (
                card.find("div", class_="n-timetable-card__auditorium").text.strip()
                if card.find("div", class_="n-timetable-card__auditorium")
                else ""
            )

            timetable_items.append(
                {
                    "date": date,
                    "time": time,
                    "subject": subject,
                    "category": category,
                    "teacher": teacher,
                    "building": building,
                    "address": address,
                    "auditorium": auditorium,
                }
            )

        return timetable_items

    def get_weekly_timetable(self, group: str) -> dict[str, list[dict[str, str]]]:
        today = datetime.now(UTC)
        start_of_week = today - timedelta(days=today.weekday())

        weekly_timetable = {}
        for i in range(7):
            date = (start_of_week + timedelta(days=i)).strftime("%Y-%m-%d")
            weekly_timetable[date] = self.parse_timetable(date, group)

        return weekly_timetable

    def save_data(self, group: str) -> None:
        file_path = Path(__file__).parent.parent / "data" / "schedule.json"
        data = self.get_weekly_timetable(group)

        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
