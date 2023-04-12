"""Test super_soco_custom setup process."""
import pytest

from homeassistant.exceptions import ConfigEntryNotReady
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.super_soco_custom import (
    SuperSocoCustomDataUpdateCoordinator,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.super_soco_custom.const import DOMAIN

from .const import MOCK_SUPER_SOCO_CONFIG


# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.
@pytest.mark.asyncio
@pytest.mark.parametrize("expected_lingering_timers", [True])
async def test_setup_unload_and_reload_entry(
    hass,
    bypass_super_soco_get_device,
    bypass_get_mapzen,
    bypass_super_soco_get_tracking_history_list,
    bypass_super_soco_get_user,
    bypass_super_soco_get_warning_list,
    bypass_super_soco_login,
):
    """Test entry setup and unload."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_SUPER_SOCO_CONFIG, entry_id="test"
    )

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be. Because we have patched the SuperSocoCustomDataUpdateCoordinator.async_get_data
    # call, no code from custom_components/super_soco_custom/super_soco_api.py actually runs.
    assert await async_setup_entry(hass, config_entry)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id])
        == SuperSocoCustomDataUpdateCoordinator
    )

    # Reload the entry and assert that the data from above is still there
    assert await async_reload_entry(hass, config_entry) is None
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id])
        == SuperSocoCustomDataUpdateCoordinator
    )

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_setup_entry_exception(hass, auth_error_on_login):
    """Test ConfigEntryNotReady when API raises an exception during entry setup."""
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_SUPER_SOCO_CONFIG, entry_id="test"
    )

    # In this case we are testing the condition where async_setup_entry raises
    # ConfigEntryNotReady using the `error_on_login` fixture which simulates
    # an error.
    with pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)
