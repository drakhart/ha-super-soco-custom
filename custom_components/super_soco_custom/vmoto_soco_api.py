import aiohttp
import async_timeout
import hashlib

__title__ = "vmoto_soco_api"
__version__ = "0.0.1"
__author__ = "@Drakhart"
__license__ = "MIT"

BASE_URL = "https://app.vmotosoco-service.com/app/v1"
JWT_PREFIX = "Quanjun "
LANGUAGE = "en"
TIMEOUT = 10
TIMEZONE = "0"
TIMEZONE_NAME = "GMT"


class VmotoSocoAPI:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        phone_prefix: int,
        phone_number: str,
        token: str = None,
    ) -> None:
        self._session = session
        self._phone_prefix = phone_prefix
        self._phone_number = phone_number
        self._token = token

    async def get_login_code(self) -> dict:
        url = f"{BASE_URL}/index/sendLogin4Code"
        headers = await self._get_headers(False)
        data = {
            "phoneCode": self._phone_prefix,
            "phone": self._phone_number,
        }

        return await self._api_wrapper(url, headers, data)

    async def get_token(self) -> str:
        return self._token

    async def get_tracking_history_list(
        self, user_id: int, device_no: str, page_num: int = 1, page_size: int = 20
    ) -> dict:
        url = f"{BASE_URL}/runTrail/list"
        headers = await self._get_headers(True)
        data = {
            "userId": user_id,
            "deviceNo": device_no,
            "pageNum": page_num,
            "pageSize": page_size,
        }

        return await self._api_wrapper(url, headers, data)

    async def get_user(self) -> dict:
        url = f"{BASE_URL}/user/index"
        headers = await self._get_headers(True)

        return await self._api_wrapper(url, headers, {})

    async def get_warning_list(
        self, user_id: int, page_num: int = 1, page_size: int = 20
    ) -> dict:
        url = f"{BASE_URL}/deviceWarn/findDeviceWarnPageByUserId"
        headers = await self._get_headers(True)
        data = {
            "userId": user_id,
            "pageNum": page_num,
            "pageSize": page_size,
        }

        return await self._api_wrapper(url, headers, data)

    async def login(self, login_code: str) -> dict:
        url = f"{BASE_URL}/index/loginByCode"
        headers = await self._get_headers(False)
        data = {
            "phoneCode": self._phone_prefix,
            "userAccount": self._phone_number,
            "loginCode": login_code,
        }

        res = await self._api_wrapper(url=url, headers=headers, data=data)
        self._token = str(res["data"]).replace(JWT_PREFIX, "")

        return res

    async def set_user_privacy(
        self, user_id: int, tracking_history: bool, push_notifications: bool
    ) -> dict:
        url = f"{BASE_URL}/user/setUserPrivacy"
        headers = await self._get_headers(True)
        data = {
            "userId": user_id,
            "historyLocusSwitch": int(tracking_history),
            "isWarnPush": int(push_notifications),
        }

        return await self._api_wrapper(url, headers, data)

    async def switch_power(self, device_no: str) -> dict:
        url = f"{BASE_URL}/device/click/{device_no}"
        headers = await self._get_headers(True)
        data = {
            "deviceNo": device_no,
        }

        return await self._api_wrapper(url, headers, data)

    async def _api_wrapper(self, url: str, headers: dict, data: dict) -> dict:
        async with async_timeout.timeout(TIMEOUT):
            res = await self._session.post(url, headers=headers, json=data)
            res.raise_for_status()
            json = await res.json()

            if json["status"] != "200":
                res.status = int(json["status"])
                res.raise_for_status()

            return json

    def _get_temp_token(self) -> str:
        unhashed = (
            LANGUAGE + str(self._phone_prefix) + self._phone_number + TIMEZONE + "QJ"
        )

        return hashlib.md5(unhashed.encode()).hexdigest().upper()

    async def _get_headers(self, authz: bool) -> dict:
        headers = {
            "content-type": "application/json; charset=UTF-8",
            "language": LANGUAGE,
            "timezone": TIMEZONE,
            "timezonename": TIMEZONE_NAME,
        }

        if authz:
            token = await self.get_token()
            headers["authorization"] = f"{JWT_PREFIX}{token}"
        else:
            headers["temptoken"] = self._get_temp_token()

        return headers
