import aiohttp
import async_timeout

__title__ = "open_street_map_api"
__version__ = "0.0.1"
__author__ = "@Drakhart"
__license__ = "MIT"

BASE_URL = "https://nominatim.openstreetmap.org"
TIMEOUT = 2


class OpenStreetMapAPI:
    def __init__(self, session: aiohttp.ClientSession, email: str) -> None:
        self._session = session
        self._email = email

    async def get_reverse(self, latitude: float, longitude: float) -> dict:
        url = f"{BASE_URL}/reverse?format=json&email={self._email}&lat={latitude}&lon={longitude}"
        headers = await self._get_headers()

        return await self._api_wrapper(url, headers)

    async def _api_wrapper(self, url: str, headers: dict = {}) -> dict:
        async with async_timeout.timeout(TIMEOUT):
            res = await self._session.get(url, headers=headers)
            res.raise_for_status()

            return await res.json()

    async def _get_headers(self) -> dict:
        return {"Content-type": "application/json; charset=UTF-8"}
