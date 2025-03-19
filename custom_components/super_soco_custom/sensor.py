import logging

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.components.sensor import SensorEntity

from .const import (
    DEFAULT_STRING,
    DOMAIN,
    SENSORS,
)
from .entity import SuperSocoCustomEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = []

    for (
        id,
        key,
        unit,
        icon,
        device_class,
        state_class,
        extra_attrs,
    ) in SENSORS:
        if key not in coordinator.data:
            _LOGGER.debug("Unable to set up sensor due to missing data key: %s", key)
        else:
            sensors.append(
                SuperSocoCustomSensor(
                    config_entry,
                    coordinator,
                    id,
                    key,
                    unit,
                    icon,
                    device_class,
                    state_class,
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
        key,
        unit,
        icon,
        device_class,
        state_class,
        extra_attrs,
    ):
        super().__init__(config_entry, coordinator)
        self._id = id
        self._key = key
        self._unit = unit
        self._icon = icon
        self._device_class = device_class
        self._state_class = state_class
        self._extra_attrs = extra_attrs

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._id}"

    @property
    def translation_key(self):
        return self._id

    @property
    def has_entity_name(self):
        return True

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key, DEFAULT_STRING)

    @property
    def native_unit_of_measurement(self):
        if self.native_value != STATE_UNAVAILABLE and self._unit is not None:
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
    def state_class(self):
        if self.native_value == STATE_UNAVAILABLE:
            return None

        return self._state_class

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
