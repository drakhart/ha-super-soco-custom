"""Tests for super_soco_custom open_street_map_api."""

import json
import pytest

from custom_components.super_soco_custom.const import OPT_EMAIL
from custom_components.super_soco_custom.open_street_map_api import (
    OpenStreetMapAPI,
    BASE_URL,
)

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from pytest_homeassistant_custom_component.common import load_fixture

from .const import MOCK_OPTIONS


@pytest.mark.asyncio
async def test_api(hass, aioclient_mock):
    """Test API calls."""

    # To test the api submodule, we first create an instance of our API client
    api = OpenStreetMapAPI(
        async_get_clientsession(hass),
        MOCK_OPTIONS[OPT_EMAIL],
    )

    # Get Mapzen
    res_mock = json.loads(load_fixture("reverse_geocoding.json"))
    latitude = 1
    longitude = 1

    aioclient_mock.get(
        f"{BASE_URL}/reverse?format=json&email={MOCK_OPTIONS[OPT_EMAIL]}&lat={latitude}&lon={longitude}",
        json=res_mock,
    )
    assert await api.get_reverse(latitude, longitude) == res_mock
