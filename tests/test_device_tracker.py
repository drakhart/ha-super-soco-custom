from unittest.mock import create_autospec

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.super_soco_custom.const import (
    DEFAULT_FLOAT,
    DEFAULT_INTEGER,
    DOMAIN,
)
from custom_components.super_soco_custom.coordinator import (
    VmotoDataUpdateCoordinator,
)
from custom_components.super_soco_custom.device_tracker import (
    VmotoDeviceTracker,
    async_setup_entry,
)

from .const import MOCK_VMOTO_CONFIG


@pytest.mark.asyncio
async def test_async_setup_entry_missing_keys(hass):
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_VMOTO_CONFIG)
    entry.add_to_hass(hass)

    # coordinator with empty data -> no device trackers created
    class Coord:
        def __init__(self):
            self.data = {}

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = Coord()

    added = []

    def async_add(entities):
        added.extend(entities)

    await async_setup_entry(hass, entry, async_add)
    assert added == []


def test_device_tracker_properties_and_extra_attrs():
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_VMOTO_CONFIG)
    coord = create_autospec(VmotoDataUpdateCoordinator, instance=True)
    coord.data = {"lat_key": 1.23, "lon_key": 4.56, "acc_key": 7, "foo": "bar"}

    device_tracker = VmotoDeviceTracker(
        entry,
        coord,
        "myid",
        "gps",
        "lat_key",
        "lon_key",
        "acc_key",
        "mdi:bike",
        {"extra": "foo"},
    )

    assert device_tracker.unique_id.endswith("myid")
    assert device_tracker.translation_key == "myid"
    assert device_tracker.has_entity_name is True
    assert device_tracker.source_type == "gps"
    assert device_tracker.latitude == 1.23
    assert device_tracker.longitude == 4.56
    assert device_tracker.gps_accuracy == 7
    assert device_tracker.icon == "mdi:bike"
    assert device_tracker.extra_state_attributes == {"extra": "bar"}


def test_device_tracker_extra_attrs_not_dict():
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_VMOTO_CONFIG)
    coord = create_autospec(VmotoDataUpdateCoordinator, instance=True)
    coord.data = {"lat_key": 1.23, "lon_key": 4.56, "acc_key": 7, "foo": "bar"}

    device_tracker = VmotoDeviceTracker(
        entry,
        coord,
        "myid",
        "gps",
        "lat_missing",
        "lon_missing",
        "acc_missing",
        "mdi:bike",
        None,
    )

    # missing keys fall back to defaults
    assert device_tracker.latitude == DEFAULT_FLOAT
    assert device_tracker.longitude == DEFAULT_FLOAT
    assert device_tracker.gps_accuracy == DEFAULT_INTEGER
    assert device_tracker.extra_state_attributes is None
