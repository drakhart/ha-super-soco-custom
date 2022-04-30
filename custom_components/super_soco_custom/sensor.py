import logging

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.components.sensor import SensorEntity

from .const import (
    DATA_MODEL_NAME,
    DEFAULT_STRING,
    DOMAIN,
    MANUFACTURER,
    SENSORS,
)
from .entity import SuperSocoCustomEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = []

    for id, name, key, unit, icon, device_class, extra_attrs in SENSORS:
        if not key in coordinator.data:
            _LOGGER.debug(f"Unable to set up sensor due to missing data key: {key}")
        else:
            sensors.append(
                SuperSocoCustomSensor(
                    config_entry,
                    coordinator,
                    id,
                    name,
                    key,
                    unit,
                    icon,
                    device_class,
                    extra_attrs,
                )
            )

    async_add_entities(sensors)


class SuperSocoCustomSensor(SuperSocoCustomEntity, SensorEntity):
    def __init__(
        self,
        config_entry,
        coordinator,
        id,
        name,
        key,
        unit,
        icon,
        device_class,
        extra_attrs,
    ):
        super().__init__(config_entry, coordinator)
        self._id = id
        self._name = name
        self._key = key
        self._unit = unit
        self._icon = icon
        self._device_class = device_class
        self._extra_attrs = extra_attrs

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._id}"

    @property
    def name(self):
        return (
            f"{MANUFACTURER} {self.coordinator.data.get(DATA_MODEL_NAME)} {self._name}"
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key, DEFAULT_STRING)

    @property
    def unit_of_measurement(self):
        if self.native_value == STATE_UNAVAILABLE:
            return None

        return self._unit

    @property
    def icon(self):
        return self._icon

    @property
    def device_class(self):
        if self.native_value == STATE_UNAVAILABLE:
            return None

        return self._device_class

    @property
    def extra_state_attributes(self):
        if type(self._extra_attrs) is dict:
            extra_attrs = {}

            for key, value in self._extra_attrs.items():
                if self.native_value == STATE_UNAVAILABLE:
                    extra_attrs[key] = STATE_UNAVAILABLE
                else:
                    extra_attrs[key] = self.coordinator.data.get(value, DEFAULT_STRING)

            return extra_attrs

        return None
