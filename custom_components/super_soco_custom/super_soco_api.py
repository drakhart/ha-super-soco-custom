import aiohttp
import async_timeout

from typing import Union

__title__ = "super_soco_api"
__version__ = "0.0.1"
__author__ = "@Drakhart"
__license__ = "MIT"

BASE_URL = "https://eg.supersocoeg.com/rest/v1"
JWT_PREFIX = "Bearer "
TIMEOUT = 5


class SuperSocoAPI:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        phone_prefix: int,
        phone_number: str,
        password: str,
        token: str = None,
    ) -> None:
        self._session = session
        self._phone_prefix = phone_prefix
        self._phone_number = phone_number
        self._password = password
        self._token = token

    async def get_device(self, device_number: str) -> dict:
        url = f"{BASE_URL}/device/info/{device_number}"
        headers = await self._get_headers(True)

        return await self._api_wrapper(url, headers)

    async def get_token(self) -> str:
        if not self._token:
            await self.login()

        return self._token

    async def get_tracking_history_list(
        self, page_num: int = 1, page_size: int = 20
    ) -> dict:
        url = f"{BASE_URL}/userRunPoint/list"
        headers = await self._get_headers(True)
        data = {
            "pageNum": page_num,
            "pageSize": page_size,
        }

        return await self._api_wrapper(url, headers, data)

    async def get_user(self) -> dict:
        url = f"{BASE_URL}/user/get"
        headers = await self._get_headers(True)

        return await self._api_wrapper(url, headers)

    async def get_warning_list(self, page_num: int = 1, page_size: int = 20) -> dict:
        url = f"{BASE_URL}/deviceWarn/list"
        headers = await self._get_headers(True)
        data = {
            "pageNum": page_num,
            "pageSize": page_size,
        }

        return await self._api_wrapper(url, headers, data)

    async def login(self) -> dict:
        url = f"{BASE_URL}/login"
        headers = await self._get_headers(False)
        data = {
            "phoneCode": self._phone_prefix,
            "phone": self._phone_number,
            "password": self._password,
        }

        res = await self._api_wrapper(url=url, headers=headers, data=data)
        self._token = str(res["data"]).replace(JWT_PREFIX, "")

        return res

    async def set_push_notifications(self, switch: bool) -> dict:
        url = f"{BASE_URL}/deviceWarn/sw/{int(switch)}"
        headers = await self._get_headers(True)

        return await self._api_wrapper(url, headers)

    async def set_tracking_history(self, switch: bool) -> dict:
        url = f"{BASE_URL}/userRunPoint/sw/{int(switch)}"
        headers = await self._get_headers(True)

        return await self._api_wrapper(url, headers)

    async def _api_wrapper(self, url: str, headers: dict = {}, data: dict = {}) -> dict:
        async with async_timeout.timeout(TIMEOUT):
            res = await self._session.post(url, headers=headers, json=data)
            res.raise_for_status()
            json = await res.json()

            if json["status"] == "403":
                await self.login()

                headers = await self._get_headers(True)

                return await self._api_wrapper(url, headers, data)
            elif json["status"] != "200":
                res.status = int(json["status"])
                res.raise_for_status()

            return json

    async def _get_headers(self, authz: bool) -> dict:
        headers = {"content-type": "application/json; charset=UTF-8"}

        if authz:
            token = await self.get_token()
            headers["authorization"] = f"{JWT_PREFIX}{token}"

        return headers
