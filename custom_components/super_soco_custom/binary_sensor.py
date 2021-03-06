import logging

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import (
    BINARY_SENSORS,
    DATA_MODEL_NAME,
    DEFAULT_INTEGER,
    DEFAULT_STRING,
    DOMAIN,
    MANUFACTURER,
)
from .entity import SuperSocoCustomEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    binary_sensors = []

    for id, name, key, condition, icon, device_class, extra_attrs in BINARY_SENSORS:
        if not key in coordinator.data:
            _LOGGER.debug(f"Unable to set up switch due to missing data key: {key}")
        else:
            binary_sensors.append(
                SuperSocoCustomBinarySensor(
                    config_entry,
                    coordinator,
                    id,
                    name,
                    key,
                    condition,
                    icon,
                    device_class,
                    extra_attrs,
                )
            )

    async_add_entities(binary_sensors)


class SuperSocoCustomBinarySensor(SuperSocoCustomEntity, BinarySensorEntity):
    def __init__(
        self,
        config_entry,
        coordinator,
        id,
        name,
        key,
        condition,
        icon,
        device_class,
        extra_attrs,
    ):
        super().__init__(config_entry, coordinator)
        self._id = id
        self._name = name
        self._key = key
        self._condition = condition
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
    def is_on(self):
        return self.coordinator.data.get(self._key, DEFAULT_INTEGER) == self._condition

    @property
    def icon(self):
        return self._icon

    @property
    def device_class(self):
        return self._device_class

    @property
    def extra_state_attributes(self):
        if type(self._extra_attrs) is dict:
            extra_attrs = {}

            for key, value in self._extra_attrs.items():
                extra_attrs[key] = self.coordinator.data.get(value, DEFAULT_STRING)

            return extra_attrs

        return None
