"""Global fixtures for vmoto integration."""

# Fixtures allow you to replace functions with a Mock object. You can perform
# many options via the Mock to reflect a particular behavior from the original
# function that you want to see without going through the function's actual logic.
# Fixtures can either be passed into tests as parameters, or if autouse=True, they
# will automatically be used across all tests.
#
# Fixtures that are defined in conftest.py are available across all tests. You can also
# define fixtures within a particular test file to scope them locally.
#
# pytest_homeassistant_custom_component provides some fixtures that are provided by
# Home Assistant core. You can find those fixture definitions here:
# https://github.com/MatthewFlamm/pytest-homeassistant-custom-component/blob/master/pytest_homeassistant_custom_component/common.py
#
# See here for more info: https://docs.pytest.org/en/latest/fixture.html (note that
# pytest includes fixtures OOB which you can use as defined on this page)
import json
from typing import cast
from unittest.mock import patch

import pytest
from aiohttp import ClientResponseError
from aiohttp.client_reqrep import RequestInfo
from multidict import (
    CIMultiDict,
    CIMultiDictProxy,
)
from pytest_homeassistant_custom_component.common import load_fixture
from yarl import URL

pytest_plugins = "pytest_homeassistant_custom_component"


# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    return


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with (
        patch("homeassistant.components.persistent_notification.async_create"),
        patch("homeassistant.components.persistent_notification.async_dismiss"),
    ):
        yield


# Fixtures to return mocked constants
@pytest.fixture(name="bypass_coordinator_switch_delay")
def bypass_coordinator_switch_delay():
    """Skip coordinator switch delay."""
    with patch(
        "custom_components.super_soco_custom.coordinator.SWITCH_REFRESH_SLEEP_SECONDS",
        0,
    ):
        yield


@pytest.fixture(name="bypass_get_mapzen")
def bypass_get_mapzen_fixture():
    """Skip calls to get Mapzen from Open Topo Data API."""
    with patch(
        "custom_components.super_soco_custom.OpenTopoDataAPI.get_mapzen",
        return_value=json.loads(load_fixture("mapzen.json")),
    ):
        yield


@pytest.fixture(name="bypass_vmoto_get_login_code")
def bypass_vmoto_get_login_code_fixture():
    """Skip calls to get login code from Vmoto API."""
    with patch(
        "custom_components.super_soco_custom.VmotoAPI.get_login_code",
        return_value=json.loads(load_fixture("vmoto_login_code.json")),
    ):
        yield


@pytest.fixture(name="bypass_vmoto_get_tracking_history_list")
def bypass_vmoto_get_tracking_history_list_fixture():
    """Skip calls to get tracking history list from Vmoto API."""
    with patch(
        "custom_components.super_soco_custom.VmotoAPI.get_tracking_history_list",
        return_value=json.loads(load_fixture("vmoto_tracking_history_list.json")),
    ):
        yield


@pytest.fixture(name="bypass_vmoto_get_user")
def bypass_vmoto_get_user_fixture():
    """Skip calls to get user from Vmoto API."""
    with patch(
        "custom_components.super_soco_custom.VmotoAPI.get_user",
        return_value=json.loads(load_fixture("vmoto_user.json")),
    ):
        yield


@pytest.fixture(name="bypass_vmoto_get_warning_list")
def bypass_vmoto_get_warning_fixture():
    """Skip calls to get warning list from Vmoto API."""
    with patch(
        "custom_components.super_soco_custom.VmotoAPI.get_warning_list",
        return_value=json.loads(load_fixture("vmoto_warning_list.json")),
    ):
        yield


@pytest.fixture(name="bypass_vmoto_login")
def bypass_vmoto_login_fixture():
    """Skip calls to login from Vmoto API."""
    with patch(
        "custom_components.super_soco_custom.VmotoAPI.login",
        return_value=json.loads(load_fixture("vmoto_login.json")),
    ):
        yield


@pytest.fixture(name="make_client_response_error")
def make_client_response_error_fixture():
    """Return a factory that creates a ClientResponseError with request_info.real_url set."""

    def _make(status=500, url="http://x"):
        req_info = RequestInfo(
            URL(url), "GET", cast("CIMultiDictProxy[str]", CIMultiDict()), URL(url)
        )
        return ClientResponseError(req_info, (), status=status)

    return _make


@pytest.fixture(name="make_fake_session")
def make_fake_session_fixture():
    """
    Factory to create a fake aiohttp-like session with queued responses.

    Usage: session = make_fake_session([({'status': '403'}, 200), ({'status': '200'}, 200)])
    Each item is a tuple (payload, status).
    """

    class FakeResponse:
        def __init__(self, payload, status=200):
            self._payload = payload
            self.status = status

        async def json(self):
            return self._payload

        def raise_for_status(self):
            if getattr(self, "status", 200) >= 400:
                raise Exception("http error")

    class FakeSession:
        def __init__(self, responses):
            # responses: list of (payload, status)
            self._responses = [FakeResponse(p, s) for p, s in responses]

        async def post(self, url, headers=None, json=None):
            return self._responses.pop(0)

    def _factory(items):
        # items is list of (payload, status)
        return FakeSession(items)

    return _factory
