"""Test super_soco_custom switch."""

import pytest

from homeassistant.components.switch.const import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON
from pytest_homeassistant_custom_component.common import MockConfigEntry
from unittest.mock import call, patch

from custom_components.super_soco_custom.const import (
    DATA_NATIVE_PUSH_NOTIFICATIONS,
    DOMAIN,
)

from .const import MOCK_SUPER_SOCO_CONFIG


@pytest.mark.asyncio
# TODO: Remove when https://github.com/home-assistant/core/pull/89976 is released
@pytest.mark.parametrize("expected_lingering_timers", [True])
async def test_switch_services(
    hass,
    bypass_coordinator_switch_delay,
    bypass_get_mapzen,
    bypass_super_soco_get_device,
    bypass_super_soco_get_user,
    bypass_super_soco_get_tracking_history_list,
    bypass_super_soco_get_warning_list,
):
    """Test switch services."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_SUPER_SOCO_CONFIG)
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Assert that the on/off services are called for push notifications switch
    with patch(
        "custom_components.super_soco_custom.SuperSocoCustomDataUpdateCoordinator.set_switch_state"
    ) as push_func:
        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_OFF,
            service_data={
                ATTR_ENTITY_ID: f"{SWITCH_DOMAIN}.super_soco_ts_native_push_notifications"
            },
            blocking=True,
        )
        assert push_func.called
        assert push_func.call_args == call(DATA_NATIVE_PUSH_NOTIFICATIONS, False)

        push_func.reset_mock()

        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_ON,
            service_data={
                ATTR_ENTITY_ID: f"{SWITCH_DOMAIN}.super_soco_ts_native_push_notifications"
            },
            blocking=True,
        )
        assert push_func.called
        assert push_func.call_args == call(DATA_NATIVE_PUSH_NOTIFICATIONS, True)

    # Assert that the on/off services are called for tracking history switch
    with patch(
        "custom_components.super_soco_custom.SuperSocoAPI.set_tracking_history"
    ) as push_func:
        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_OFF,
            service_data={
                ATTR_ENTITY_ID: f"{SWITCH_DOMAIN}.super_soco_ts_native_tracking_history"
            },
            blocking=True,
        )
        assert push_func.called
        assert push_func.call_args == call(False)

        push_func.reset_mock()

        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_ON,
            service_data={
                ATTR_ENTITY_ID: f"{SWITCH_DOMAIN}.super_soco_ts_native_tracking_history"
            },
            blocking=True,
        )
        assert push_func.called
        assert push_func.call_args == call(True)

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
