import pytest
from unittest.mock import create_autospec

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.super_soco_custom.binary_sensor import (
    SuperSocoCustomBinarySensor,
)
from custom_components.super_soco_custom.const import DOMAIN
from custom_components.super_soco_custom.coordinator import (
    SuperSocoCustomDataUpdateCoordinator,
)

from .const import MOCK_SUPER_SOCO_CONFIG


@pytest.mark.asyncio
async def test_binary_sensor_properties():
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_SUPER_SOCO_CONFIG)
    coord = create_autospec(SuperSocoCustomDataUpdateCoordinator, instance=True)
    coord.data = {"foo": 1, "bar": "baz"}

    binary_sensor = SuperSocoCustomBinarySensor(
        entry, coord, "myid", "foo", 1, "ic", "device", {"x": "bar"}
    )

    assert binary_sensor.unique_id == f"{DOMAIN}_myid"
    assert binary_sensor.translation_key == "myid"
    assert binary_sensor.is_on is True
    assert binary_sensor.icon == "ic"
    assert binary_sensor.device_class == "device"
    assert binary_sensor.extra_state_attributes == {"x": "baz"}


@pytest.mark.asyncio
async def test_binary_sensor_missing_key():
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_SUPER_SOCO_CONFIG)
    coord = create_autospec(SuperSocoCustomDataUpdateCoordinator, instance=True)
    coord.data = {}

    binary_sensor = SuperSocoCustomBinarySensor(
        entry, coord, "myid", "missing", 1, "ic", "device", None
    )

    assert binary_sensor.is_on is False
    assert binary_sensor.extra_state_attributes is None
