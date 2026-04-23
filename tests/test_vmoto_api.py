"""Tests for vmoto vmoto_api."""

import json
from unittest.mock import MagicMock

import aiohttp
import pytest
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.super_soco_custom.const import (
    CONF_LOGIN_CODE,
    CONF_PHONE_NUMBER,
    CONF_PHONE_PREFIX,
)
from custom_components.super_soco_custom.vmoto_api import BASE_URL, VmotoAPI

from .const import MOCK_DEVICE_NO, MOCK_USER_ID, MOCK_VMOTO_CONFIG


@pytest.mark.asyncio
async def test_api(hass, aioclient_mock):
    """Test API calls."""
    # To test the api submodule, we first create an instance of our API client
    api = VmotoAPI(
        async_get_clientsession(hass),
        MOCK_VMOTO_CONFIG[CONF_PHONE_PREFIX],
        MOCK_VMOTO_CONFIG[CONF_PHONE_NUMBER],
    )

    # Temp token
    assert api._get_temp_token() == "1061DF687283FB6D662830C0B542D942"

    # Login code
    res_mock = json.loads(load_fixture("vmoto_login_code.json"))

    aioclient_mock.post(f"{BASE_URL}/index/sendLogin4Code", json=res_mock)
    assert await api.get_login_code() == res_mock

    # Login
    res_mock = json.loads(load_fixture("vmoto_login.json"))

    aioclient_mock.post(f"{BASE_URL}/index/loginByCode", json=res_mock)
    assert await api.login(MOCK_VMOTO_CONFIG[CONF_LOGIN_CODE]) == res_mock

    # Get tracking history list
    res_mock = json.loads(load_fixture("vmoto_tracking_history_list.json"))

    aioclient_mock.post(f"{BASE_URL}/runTrail/list", json=res_mock)
    assert (
        await api.get_tracking_history_list(MOCK_USER_ID, MOCK_DEVICE_NO, 1, 1)
        == res_mock
    )

    # Get user
    res_mock = json.loads(load_fixture("vmoto_user.json"))

    aioclient_mock.post(f"{BASE_URL}/user/index", json=res_mock)
    assert await api.get_user() == res_mock

    # Get warning list
    res_mock = json.loads(load_fixture("vmoto_warning_list.json"))

    aioclient_mock.post(
        f"{BASE_URL}/deviceWarn/findDeviceWarnPageByUserId", json=res_mock
    )
    assert await api.get_warning_list(MOCK_USER_ID, 1, 1) == res_mock

    # Set user privacy
    res_mock = json.loads(load_fixture("vmoto_user_privacy.json"))

    aioclient_mock.post(f"{BASE_URL}/user/setUserPrivacy", json=res_mock)
    assert await api.set_user_privacy(MOCK_USER_ID, True, False) == res_mock

    # Switch power
    res_mock = json.loads(load_fixture("vmoto_switch_power.json"))

    aioclient_mock.post(f"{BASE_URL}/device/click/{MOCK_DEVICE_NO}", json=res_mock)
    assert await api.switch_power(MOCK_DEVICE_NO) == res_mock


def test_api_raises_value_error_without_credentials():
    """VmotoAPI raises ValueError when neither email nor phone params are provided."""
    session = MagicMock(spec=aiohttp.ClientSession)

    with pytest.raises(ValueError, match="Either email or both phone_prefix"):
        VmotoAPI(session)


@pytest.mark.asyncio
async def test_email_api(hass, aioclient_mock):
    """Test email-based API methods."""
    api = VmotoAPI(
        async_get_clientsession(hass),
        email="test@example.com",
    )

    # Temp token with email
    token = api._get_temp_token()
    assert isinstance(token, str) and len(token) == 32

    # get_login_code with email → calls get_email_login_code
    res_mock = json.loads(load_fixture("vmoto_login_code.json"))
    aioclient_mock.post(f"{BASE_URL}/index/sendEmailLoginCode", json=res_mock)
    assert await api.get_login_code() == res_mock

    # email_login
    res_mock = json.loads(load_fixture("vmoto_login.json"))
    aioclient_mock.post(f"{BASE_URL}/index/emailLoginByCode", json=res_mock)
    result = await api.email_login(MOCK_VMOTO_CONFIG[CONF_LOGIN_CODE])
    assert result == res_mock
    # token extracted from login response
    assert api.get_token() is not None

    # login with email → delegates to email_login
    res_mock2 = json.loads(load_fixture("vmoto_login.json"))
    aioclient_mock.post(f"{BASE_URL}/index/emailLoginByCode", json=res_mock2)
    result2 = await api.login(MOCK_VMOTO_CONFIG[CONF_LOGIN_CODE])
    assert result2 == res_mock2
