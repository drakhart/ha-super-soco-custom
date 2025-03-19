"""Test super_soco_custom config flow."""

import pytest

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry
from unittest.mock import patch

from custom_components.super_soco_custom.const import (
    CONF_APP_NAME,
    CONF_LOGIN_CODE,
    CONF_PHONE_NUMBER,
    CONF_PHONE_PREFIX,
    CONF_PASSWORD,
    DOMAIN,
    NAME,
    OPT_EMAIL,
    OPT_ENABLE_ALTITUDE_ENTITY,
    OPT_ENABLE_LAST_TRIP_ENTITIES,
    OPT_ENABLE_LAST_WARNING_ENTITY,
    OPT_ENABLE_REVERSE_GEOCODING_ENTITY,
    OPT_UPDATE_INTERVAL,
)

from .const import MOCK_SUPER_SOCO_CONFIG, MOCK_VMOTO_SOCO_CONFIG


# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with (
        patch(
            "custom_components.super_soco_custom.async_setup",
            return_value=True,
        ),
        patch(
            "custom_components.super_soco_custom.async_setup_entry",
            return_value=True,
        ),
    ):
        yield


# Here we simulate a successful Super Soco config flow from the backend.
# Note that we use the `bypass_super_soco_login` fixture here because
# we want the config flow validation to succeed during the test.
@pytest.mark.asyncio
async def test_successful_super_soco_config_flow(
    hass,
    bypass_super_soco_login,
):
    """Test a successful Super Soco config flow."""
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "app"

    # Continue past the app step
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_APP_NAME: MOCK_SUPER_SOCO_CONFIG[CONF_APP_NAME],
            CONF_PHONE_NUMBER: MOCK_SUPER_SOCO_CONFIG[CONF_PHONE_NUMBER],
            CONF_PHONE_PREFIX: MOCK_SUPER_SOCO_CONFIG[CONF_PHONE_PREFIX],
        },
    )

    # Check that the config flow shows the login form as the next step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "login"

    # Continue past the login step
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_PASSWORD: MOCK_SUPER_SOCO_CONFIG[CONF_PASSWORD]},
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == NAME
    assert result["data"] == MOCK_SUPER_SOCO_CONFIG
    assert result["result"]


# Here we simulate a successful Vmoto Soco config flow from the backend.
# Note that we use the `bypass_vmoto_soco_get_login_code` and
# `bypass_vmoto_soco_login` fixture here because we want the config flow
# validation to succeed during the test.
@pytest.mark.asyncio
async def test_successful_vmoto_soco_config_flow(
    hass,
    bypass_vmoto_soco_get_login_code,
    bypass_vmoto_soco_login,
):
    """Test a successful Vmoto Soco config flow."""
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "app"

    # Continue past the app step
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_APP_NAME: MOCK_VMOTO_SOCO_CONFIG[CONF_APP_NAME],
            CONF_PHONE_NUMBER: MOCK_VMOTO_SOCO_CONFIG[CONF_PHONE_NUMBER],
            CONF_PHONE_PREFIX: MOCK_VMOTO_SOCO_CONFIG[CONF_PHONE_PREFIX],
        },
    )

    # Check that the config flow shows the login form as the next step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "login"

    # Continue past the login step
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_LOGIN_CODE: MOCK_VMOTO_SOCO_CONFIG[CONF_LOGIN_CODE]},
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == NAME
    assert result["data"] == MOCK_VMOTO_SOCO_CONFIG
    assert result["result"]


# In this case, we want to simulate a failure during the config flow.
# We use the `auth_error_on_login` (note the function parameters) to
# raise an Exception during validation of the input config.
@pytest.mark.asyncio
async def test_failed_config_flow(
    hass,
    auth_error_on_login,
):
    """Test a failed config flow due to credential validation failure."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_APP_NAME: MOCK_SUPER_SOCO_CONFIG[CONF_APP_NAME],
            CONF_PHONE_NUMBER: MOCK_SUPER_SOCO_CONFIG[CONF_PHONE_NUMBER],
            CONF_PHONE_PREFIX: MOCK_SUPER_SOCO_CONFIG[CONF_PHONE_PREFIX],
        },
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_PASSWORD: MOCK_SUPER_SOCO_CONFIG[CONF_PASSWORD]},
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


# Our config flow also has an options flow, so we must test it as well.
@pytest.mark.asyncio
async def test_options_flow(hass):
    """Test an options flow."""
    # Create a new MockConfigEntry and add to HASS (we're bypassing config
    # flow entirely)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_SUPER_SOCO_CONFIG, entry_id="test")
    entry.add_to_hass(hass)

    # Initialize an options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    # Verify that the first options step is a user form
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # Enter some fake data into the form
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            OPT_UPDATE_INTERVAL: 5,
        },
    )

    # Verify that the flow finishes
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == NAME

    # Verify that the options were updated
    assert entry.options == {
        OPT_UPDATE_INTERVAL: 5,
        OPT_EMAIL: "",
        OPT_ENABLE_ALTITUDE_ENTITY: True,
        OPT_ENABLE_LAST_TRIP_ENTITIES: True,
        OPT_ENABLE_LAST_WARNING_ENTITY: True,
        OPT_ENABLE_REVERSE_GEOCODING_ENTITY: False,
    }
