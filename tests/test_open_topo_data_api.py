"""Tests for super_soco_custom open_topo_data_api."""

import json
import pytest

from custom_components.super_soco_custom.open_topo_data_api import (
    OpenTopoDataAPI,
    BASE_URL,
)

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from pytest_homeassistant_custom_component.common import load_fixture


@pytest.mark.asyncio
async def test_api(hass, aioclient_mock):
    """Test API calls."""

    # To test the api submodule, we first create an instance of our API client
    api = OpenTopoDataAPI(async_get_clientsession(hass))

    # Get Mapzen
    res_mock = json.loads(load_fixture("mapzen.json"))

    aioclient_mock.get(f"{BASE_URL}/mapzen?locations=1,1", json=res_mock)
    assert await api.get_mapzen(1, 1) == res_mock
