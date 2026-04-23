"""Test vmoto setup process."""

import pytest
from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ConfigEntryNotReady
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.super_soco_custom import (
    VmotoDataUpdateCoordinator,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.super_soco_custom.const import DOMAIN

from .const import MOCK_VMOTO_CONFIG


# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.
@pytest.mark.asyncio
async def test_setup_reload_and_unload_entry(
    hass,
    bypass_get_mapzen,
    bypass_vmoto_get_user,
    bypass_vmoto_get_tracking_history_list,
    bypass_vmoto_get_warning_list,
):
    """Test entry setup and unload."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_VMOTO_CONFIG,
        entry_id="test",
        state=ConfigEntryState.LOADED,
    )

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be. Because we have patched the VmotoDataUpdateCoordinator.async_get_data
    # call, no code from custom_components/vmoto/vmoto_api.py actually runs.
    assert await async_setup_entry(hass, config_entry)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert type(hass.data[DOMAIN][config_entry.entry_id]) is VmotoDataUpdateCoordinator

    # Reload the entry and assert that the data from above is still there
    assert await async_reload_entry(hass, config_entry) is None
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert type(hass.data[DOMAIN][config_entry.entry_id]) is VmotoDataUpdateCoordinator

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_setup_entry_raises_config_entry_not_ready_when_coordinator_fails(hass):
    """async_setup_entry should raise ConfigEntryNotReady when coordinator refresh fails."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_VMOTO_CONFIG,
        entry_id="test_fail",
    )

    async def failing_refresh(self):
        self.last_update_success = False

    with patch(
        "custom_components.super_soco_custom.VmotoDataUpdateCoordinator.async_refresh",
        failing_refresh,
    ):
        with pytest.raises(ConfigEntryNotReady):
            await async_setup_entry(hass, config_entry)
