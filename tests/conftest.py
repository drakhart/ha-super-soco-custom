"""Global fixtures for super_soco_custom integration."""
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
import pytest

from pytest_homeassistant_custom_component.common import load_fixture

from unittest.mock import patch

from custom_components.super_soco_custom.config_flow import InvalidAuth

pytest_plugins = "pytest_homeassistant_custom_component"


# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
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


# Fixtures to return mocked data from API calls
@pytest.fixture(name="bypass_super_soco_get_device")
def bypass_super_soco_get_device_fixture():
    """Skip calls to get device from Super Soco API."""
    with patch(
        "custom_components.super_soco_custom.SuperSocoAPI.get_device",
        return_value=json.loads(load_fixture("super_soco_device.json")),
    ):
        yield


@pytest.fixture(name="bypass_get_mapzen")
def bypass_get_mapzen():
    """Skip calls to get Mapzen from Open Topo Data API."""
    with patch(
        "custom_components.super_soco_custom.OpenTopoDataAPI.get_mapzen",
        return_value=json.loads(load_fixture("mapzen.json")),
    ):
        yield


@pytest.fixture(name="bypass_super_soco_get_tracking_history_list")
def bypass_super_soco_get_tracking_history_list_fixture():
    """Skip calls to get tracking history list from Super Soco API."""
    with patch(
        "custom_components.super_soco_custom.SuperSocoAPI.get_tracking_history_list",
        return_value=json.loads(load_fixture("super_soco_tracking_history_list.json")),
    ):
        yield


@pytest.fixture(name="bypass_super_soco_get_user")
def bypass_super_soco_get_user_fixture():
    """Skip calls to get user from Super Soco API."""
    with patch(
        "custom_components.super_soco_custom.SuperSocoAPI.get_user",
        return_value=json.loads(load_fixture("super_soco_user.json")),
    ):
        yield


@pytest.fixture(name="bypass_super_soco_get_warning_list")
def bypass_super_soco_get_warning_fixture():
    """Skip calls to get warning list from Super Soco API."""
    with patch(
        "custom_components.super_soco_custom.SuperSocoAPI.get_warning_list",
        return_value=json.loads(load_fixture("super_soco_warning_list.json")),
    ):
        yield


@pytest.fixture(name="bypass_super_soco_login")
def bypass_super_soco_login_fixture():
    """Skip calls to login from Super Soco API."""
    with patch(
        "custom_components.super_soco_custom.SuperSocoAPI.login",
        return_value=json.loads(load_fixture("super_soco_login.json")),
    ):
        yield


@pytest.fixture(name="bypass_vmoto_soco_get_login_code")
def bypass_vmoto_soco_get_login_code_fixture():
    """Skip calls to get login code from Vmoto Soco API."""
    with patch(
        "custom_components.super_soco_custom.VmotoSocoAPI.get_login_code",
        return_value=json.loads(load_fixture("vmoto_soco_login_code.json")),
    ):
        yield


@pytest.fixture(name="bypass_vmoto_soco_get_tracking_history_list")
def bypass_vmoto_soco_get_tracking_history_list_fixture():
    """Skip calls to get tracking history list from Super Soco API."""
    with patch(
        "custom_components.super_soco_custom.VmotoSocoAPI.get_tracking_history_list",
        return_value=json.loads(load_fixture("vmoto_soco_tracking_history_list.json")),
    ):
        yield


@pytest.fixture(name="bypass_vmoto_soco_get_user")
def bypass_vmoto_soco_get_user_fixture():
    """Skip calls to get user from Vmoto Soco API."""
    with patch(
        "custom_components.super_soco_custom.VmotoSocoAPI.get_user",
        return_value=json.loads(load_fixture("vmoto_soco_user.json")),
    ):
        yield


@pytest.fixture(name="bypass_vmoto_soco_get_warning_list")
def bypass_vmoto_soco_get_warning_fixture():
    """Skip calls to get warning list from Super Soco API."""
    with patch(
        "custom_components.super_soco_custom.VmotoSocoAPI.get_warning_list",
        return_value=json.loads(load_fixture("vmoto_soco_warning_list.json")),
    ):
        yield


@pytest.fixture(name="bypass_vmoto_soco_login")
def bypass_vmoto_soco_login_fixture():
    """Skip calls to login from Vmoto Soco API."""
    with patch(
        "custom_components.super_soco_custom.VmotoSocoAPI.login",
        return_value=json.loads(load_fixture("vmoto_soco_login.json")),
    ):
        yield


# Fixtures to return exceptions from API calls
@pytest.fixture(name="auth_error_on_login")
def auth_error_login_fixture():
    """Simulate auth error when logging in to Super Soco API."""
    with patch(
        "custom_components.super_soco_custom.SuperSocoAPI.login",
        side_effect=InvalidAuth,
    ):
        yield
