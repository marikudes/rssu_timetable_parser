import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

import aiohttp
from bs4 import BeautifulSoup

from .config import headers, timetableparams, timetableurl


class TimeTableParser:
    async def response(
        self,
        session: aiohttp.ClientSession,
        date: str,
        group: str,
    ) -> dict[str, Any]:
        params = timetableparams.copy()
        params["date"] = date
        params["group"] = group

        async with session.post(timetableurl, headers=headers, data=params, ssl=False) as response:
            text = await response.text()
            try:
                return cast("dict[str, Any]", json.loads(text))
            except json.JSONDecodeError as e:
                raise ValueError(f"Expected JSON:\n{text[:300]}") from e

    async def parse_timetable(
        self,
        session: aiohttp.ClientSession,
        date: str,
        group: str,
    ) -> list[dict[str, str]]:
        data = await self.response(session, date, group)
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

    async def get_weekly_timetable(self, group: str) -> dict[str, list[dict[str, str]]]:
        today = datetime.now(UTC)
        start_of_week = today - timedelta(days=today.weekday())

        dates = [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            tasks = [self.parse_timetable(session, date, group) for date in dates]
            results = await asyncio.gather(*tasks)

            # Используем словарное включение вместо цикла
            timetable: dict[str, list[dict[str, str]]] = dict(zip(dates, results, strict=False))

            return timetable

    async def save_data(self, group: str) -> None:
        file_path = Path(__file__).parent.parent / "data" / "schedule.json"
        data = await self.get_weekly_timetable(group)
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def save_data_sync(self, group: str) -> None:
        asyncio.run(self.save_data(group))
