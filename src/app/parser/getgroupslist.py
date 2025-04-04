import asyncio
import json
from pathlib import Path
from typing import Any, cast

import aiohttp

from .config import getgrouplisturl, headers


class GroupListParser:
    async def response(self, session: aiohttp.ClientSession) -> dict[str, Any]:
        async with session.post(getgrouplisturl, headers=headers, ssl=False) as response:
            text = await response.text()
            try:
                return cast("dict[str, Any]", json.loads(text))
            except json.JSONDecodeError as e:
                raise ValueError(f"Expected JSON but got:\n{text[:300]}") from e

    async def save_data(self) -> None:
        json_path = Path(__file__).parent.parent / "data" / "groups.json"
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            data = await self.response(session)
            with json_path.open("w", encoding="utf-8") as file:
                suggestions = data.get("suggestions", [])
                json.dump(suggestions, file, ensure_ascii=False, indent=4)

    def save_data_sync(self) -> None:
        asyncio.run(self.save_data())
