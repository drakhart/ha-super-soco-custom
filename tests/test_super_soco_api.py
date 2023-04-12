"""Tests for super_soco_custom super_soco_api."""
import json
import pytest

from custom_components.super_soco_custom.const import (
    CONF_PHONE_PREFIX,
    CONF_PHONE_NUMBER,
    CONF_PASSWORD,
)
from custom_components.super_soco_custom.super_soco_api import SuperSocoAPI, BASE_URL

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from pytest_homeassistant_custom_component.common import load_fixture

from .const import MOCK_SUPER_SOCO_CONFIG


@pytest.mark.asyncio
async def test_api(hass, aioclient_mock):
    """Test API calls."""

    # To test the api submodule, we first create an instance of our API client
    api = SuperSocoAPI(
        async_get_clientsession(hass),
        MOCK_SUPER_SOCO_CONFIG[CONF_PHONE_PREFIX],
        MOCK_SUPER_SOCO_CONFIG[CONF_PHONE_NUMBER],
        MOCK_SUPER_SOCO_CONFIG[CONF_PASSWORD],
    )

    # Login
    res_mock = json.loads(load_fixture("super_soco_login.json"))

    aioclient_mock.post(f"{BASE_URL}/login", json=res_mock)
    assert await api.login() == res_mock

    # Get device
    res_mock = json.loads(load_fixture("super_soco_device.json"))

    aioclient_mock.post(f"{BASE_URL}/device/info/1234567890123456", json=res_mock)
    assert await api.get_device(1234567890123456) == res_mock

    # Get tracking history list
    res_mock = json.loads(load_fixture("super_soco_tracking_history_list.json"))

    aioclient_mock.post(f"{BASE_URL}/userRunPoint/list", json=res_mock)
    assert await api.get_tracking_history_list(1, 1) == res_mock

    # Get user
    res_mock = json.loads(load_fixture("super_soco_user.json"))

    aioclient_mock.post(f"{BASE_URL}/user/get", json=res_mock)
    assert await api.get_user() == res_mock

    # Get warning list
    res_mock = json.loads(load_fixture("super_soco_warning_list.json"))

    aioclient_mock.post(f"{BASE_URL}/deviceWarn/list", json=res_mock)
    assert await api.get_warning_list(1, 1) == res_mock

    # Set push notifications
    res_mock = json.loads(load_fixture("super_soco_push_notifications.json"))

    aioclient_mock.post(f"{BASE_URL}/deviceWarn/sw/1", json=res_mock)
    assert await api.set_push_notifications(True) == res_mock

    # Set tracking history
    res_mock = json.loads(load_fixture("super_soco_tracking_history.json"))

    aioclient_mock.post(f"{BASE_URL}/userRunPoint/sw/1", json=res_mock)
    assert await api.set_tracking_history(True) == res_mock
