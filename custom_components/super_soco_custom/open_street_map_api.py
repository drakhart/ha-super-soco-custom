import aiohttp
from asyncio import timeout

__title__ = "open_street_map_api"
__version__ = "0.0.1"
__author__ = "@Drakhart"
__license__ = "MIT"

BASE_URL = "https://nominatim.openstreetmap.org"
TIMEOUT = 10


class OpenStreetMapAPI:
    def __init__(self, session: aiohttp.ClientSession, email: str | None) -> None:
        self._session = session
        self._email: str | None = email

    async def get_reverse(self, latitude: float, longitude: float) -> dict:
        # Only include the email parameter if provided
        email_param = f"&email={self._email}" if self._email else ""
        url = f"{BASE_URL}/reverse?format=json{email_param}&lat={latitude}&lon={longitude}"
        headers = self._get_headers()

        return await self._api_wrapper(url, headers)

    async def _api_wrapper(self, url: str, headers: dict) -> dict:
        async with timeout(TIMEOUT):
            res = await self._session.get(url, headers=headers)
            res.raise_for_status()

            return await res.json()

    def _get_headers(self) -> dict:
        return {"Content-type": "application/json; charset=UTF-8"}
