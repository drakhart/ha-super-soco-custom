"""Tests for vmoto sensor."""

from unittest.mock import create_autospec

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import STATE_UNAVAILABLE
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.super_soco_custom.const import (
    DATA_BATTERY,
    DOMAIN,
)
from custom_components.super_soco_custom.coordinator import VmotoDataUpdateCoordinator
from custom_components.super_soco_custom.sensor import VmotoSensor, async_setup_entry

from .const import MOCK_VMOTO_CONFIG


def _make_sensor(
    data, key, unit=None, device_class=None, state_class=None, extra_attrs=None
):
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_VMOTO_CONFIG)
    coord = create_autospec(VmotoDataUpdateCoordinator, instance=True)
    coord.data = data
    return VmotoSensor(
        entry,
        coord,
        "sid",
        key,
        unit,
        "mdi:test",
        device_class,
        state_class,
        extra_attrs,
    )


@pytest.mark.asyncio
async def test_async_setup_entry_skips_missing_key(hass):
    """async_setup_entry logs and skips sensors whose key is absent from coordinator.data."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_VMOTO_CONFIG, entry_id="test")

    coord = create_autospec(VmotoDataUpdateCoordinator, instance=True)
    coord.data = {}

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coord

    added = []
    await async_setup_entry(hass, entry, lambda entities: added.extend(entities))

    # All sensor keys are absent → no entities added
    assert added == []


def test_native_unit_of_measurement_returns_unit_when_value_is_not_unavailable():
    """native_unit_of_measurement returns the unit when value is not STATE_UNAVAILABLE."""
    sensor = _make_sensor({DATA_BATTERY: 80}, DATA_BATTERY, unit="% ")
    assert sensor.native_unit_of_measurement == "% "


def test_native_unit_of_measurement_returns_none_when_unit_is_none():
    """native_unit_of_measurement returns None when unit is None."""
    sensor = _make_sensor({DATA_BATTERY: 80}, DATA_BATTERY, unit=None)
    assert sensor.native_unit_of_measurement is None


def test_device_class_returns_none_when_state_unavailable():
    """device_class returns None when native_value is STATE_UNAVAILABLE."""
    sensor = _make_sensor(
        {DATA_BATTERY: STATE_UNAVAILABLE},
        DATA_BATTERY,
        device_class=SensorDeviceClass.BATTERY,
    )
    assert sensor.device_class is None


def test_device_class_returns_value_when_not_unavailable():
    """device_class returns the device class when value is not STATE_UNAVAILABLE."""
    sensor = _make_sensor(
        {DATA_BATTERY: 80}, DATA_BATTERY, device_class=SensorDeviceClass.BATTERY
    )
    assert sensor.device_class == SensorDeviceClass.BATTERY


def test_state_class_returns_none_when_state_unavailable():
    """state_class returns None when native_value is STATE_UNAVAILABLE."""
    sensor = _make_sensor(
        {DATA_BATTERY: STATE_UNAVAILABLE},
        DATA_BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    )
    assert sensor.state_class is None


def test_state_class_returns_value_when_not_unavailable():
    """state_class returns the state class when value is not STATE_UNAVAILABLE."""
    sensor = _make_sensor(
        {DATA_BATTERY: 80}, DATA_BATTERY, state_class=SensorStateClass.MEASUREMENT
    )
    assert sensor.state_class == SensorStateClass.MEASUREMENT


def test_extra_state_attributes_with_unavailable_value():
    """extra_state_attributes sets STATE_UNAVAILABLE for each key when value is unavailable."""
    sensor = _make_sensor(
        {DATA_BATTERY: STATE_UNAVAILABLE},
        DATA_BATTERY,
        extra_attrs={"attr_key": "some_other_key"},
    )
    result = sensor.extra_state_attributes
    assert result == {"attr_key": STATE_UNAVAILABLE}


def test_extra_state_attributes_returns_none_when_not_dict():
    """extra_state_attributes returns None when extra_attrs is not a dict."""
    sensor = _make_sensor({DATA_BATTERY: 80}, DATA_BATTERY, extra_attrs=None)
    assert sensor.extra_state_attributes is None


def test_extra_state_attributes_returns_none_when_extra_attrs_is_list():
    """extra_state_attributes returns None when extra_attrs is a list (not a dict)."""
    sensor = _make_sensor({DATA_BATTERY: 80}, DATA_BATTERY, extra_attrs=["x", "y"])
    assert sensor.extra_state_attributes is None


def test_extra_state_attributes_dict_with_normal_value():
    """extra_state_attributes fetches data from coordinator when value is not STATE_UNAVAILABLE."""
    sensor = _make_sensor(
        {DATA_BATTERY: 80, "other_key": "hello"},
        DATA_BATTERY,
        extra_attrs={"my_attr": "other_key"},
    )
    result = sensor.extra_state_attributes
    assert result == {"my_attr": "hello"}


def test_sensor_icon():
    """icon returns the icon value passed at construction."""
    sensor = _make_sensor({DATA_BATTERY: 80}, DATA_BATTERY)
    assert sensor.icon == "mdi:test"
