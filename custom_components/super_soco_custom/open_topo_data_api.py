import aiohttp
import async_timeout

__title__ = "open_topo_data_api"
__version__ = "0.0.1"
__author__ = "@Drakhart"
__license__ = "MIT"

BASE_URL = "https://api.opentopodata.org/v1"
TIMEOUT = 3


class OpenTopoDataAPI:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def get_mapzen(self, latitude: float, longitude: float) -> dict:
        url = f"{BASE_URL}/mapzen?locations={latitude},{longitude}"
        headers = await self._get_headers()

        return await self._api_wrapper(url, headers)

    async def _api_wrapper(self, url: str, headers: dict = {}) -> dict:
        async with async_timeout.timeout(TIMEOUT):
            res = await self._session.get(url, headers=headers)
            res.raise_for_status()

            return await res.json()

    async def _get_headers(self) -> dict:
        return {"Content-type": "application/json; charset=UTF-8"}
