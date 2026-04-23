"""Test vmoto switch."""

from unittest.mock import AsyncMock, create_autospec

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.super_soco_custom.const import (
    DOMAIN,
)
from custom_components.super_soco_custom.coordinator import (
    VmotoDataUpdateCoordinator,
)
from custom_components.super_soco_custom.switch import (
    VmotoSwitch,
)

from .const import MOCK_VMOTO_CONFIG


def test_switch_extra_state_attributes_mapping():
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_VMOTO_CONFIG)
    coord = create_autospec(VmotoDataUpdateCoordinator, instance=True)
    coord.data = {"a": "one", "b": "two"}

    switch = VmotoSwitch(entry, coord, "sid", "a", 1, "ic", {"x": "b"})

    assert switch.extra_state_attributes == {"x": "two"}


@pytest.mark.asyncio
async def test_switch_turns_call_coordinator():
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_VMOTO_CONFIG)
    coord = create_autospec(VmotoDataUpdateCoordinator, instance=True)
    coord.data = {"k": 0}
    coord.set_switch_state = AsyncMock()

    switch = VmotoSwitch(entry, coord, "sid", "k", 1, "ic", None)

    await switch.async_turn_on()
    await switch.async_turn_off()

    assert coord.set_switch_state.await_args_list == [
        (("k", True),),
        (("k", False),),
    ]


@pytest.mark.asyncio
async def test_async_setup_entry_skips_missing_key(hass):
    """async_setup_entry logs and skips switches whose key is absent from coordinator.data."""
    from custom_components.super_soco_custom.switch import async_setup_entry

    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_VMOTO_CONFIG, entry_id="test")

    coord = create_autospec(VmotoDataUpdateCoordinator, instance=True)
    coord.data = {}

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coord

    added = []
    await async_setup_entry(hass, entry, lambda entities: added.extend(entities))

    assert added == []


def test_switch_is_on():
    """is_on returns True when data matches condition."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_VMOTO_CONFIG)
    coord = create_autospec(VmotoDataUpdateCoordinator, instance=True)
    coord.data = {"k": 1}

    switch = VmotoSwitch(entry, coord, "sid", "k", 1, "mdi:test", None)

    assert switch.is_on is True
    coord.data = {"k": 0}
    assert switch.is_on is False


def test_switch_icon():
    """icon returns the icon value passed at construction."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_VMOTO_CONFIG)
    coord = create_autospec(VmotoDataUpdateCoordinator, instance=True)
    coord.data = {}

    switch = VmotoSwitch(entry, coord, "sid", "k", 1, "mdi:power", None)

    assert switch.icon == "mdi:power"


def test_switch_extra_state_attributes_returns_none_when_not_dict():
    """extra_state_attributes returns None when extra_attrs is not a dict."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_VMOTO_CONFIG)
    coord = create_autospec(VmotoDataUpdateCoordinator, instance=True)
    coord.data = {"k": 1}

    switch = VmotoSwitch(entry, coord, "sid", "k", 1, "ic", None)

    assert switch.extra_state_attributes is None
