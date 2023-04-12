"""Test super_soco_custom switch."""
import pytest

from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.const import Platform, ATTR_ENTITY_ID

from pytest_homeassistant_custom_component.common import MockConfigEntry

from unittest.mock import call, patch

from custom_components.super_soco_custom.const import DOMAIN

from .const import MOCK_CONFIG


@pytest.mark.asyncio
@pytest.mark.parametrize("expected_lingering_timers", [True])
async def test_switch_services(
    hass,
    bypass_get_device,
    bypass_get_mapzen,
    bypass_get_tracking_history_list,
    bypass_get_user,
    bypass_get_warning_list,
    bypass_login,
):
    """Test switch services."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Assert that the on/off services are called for push notifications switch
    with patch(
        "custom_components.super_soco_custom.SuperSocoAPI.set_push_notifications"
    ) as push_func:
        await hass.services.async_call(
            Platform.SWITCH,
            SERVICE_TURN_OFF,
            service_data={
                ATTR_ENTITY_ID: f"{Platform.SWITCH}.super_soco_ts_native_push_notifications"
            },
            blocking=True,
        )
        assert push_func.called
        assert push_func.call_args == call(False)

        push_func.reset_mock()

        await hass.services.async_call(
            Platform.SWITCH,
            SERVICE_TURN_ON,
            service_data={
                ATTR_ENTITY_ID: f"{Platform.SWITCH}.super_soco_ts_native_push_notifications"
            },
            blocking=True,
        )
        assert push_func.called
        assert push_func.call_args == call(True)

    # Assert that the on/off services are called for tracking history switch
    with patch(
        "custom_components.super_soco_custom.SuperSocoAPI.set_tracking_history"
    ) as push_func:
        await hass.services.async_call(
            Platform.SWITCH,
            SERVICE_TURN_OFF,
            service_data={
                ATTR_ENTITY_ID: f"{Platform.SWITCH}.super_soco_ts_native_tracking_history"
            },
            blocking=True,
        )
        assert push_func.called
        assert push_func.call_args == call(False)

        push_func.reset_mock()

        await hass.services.async_call(
            Platform.SWITCH,
            SERVICE_TURN_ON,
            service_data={
                ATTR_ENTITY_ID: f"{Platform.SWITCH}.super_soco_ts_native_tracking_history"
            },
            blocking=True,
        )
        assert push_func.called
        assert push_func.call_args == call(True)

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
