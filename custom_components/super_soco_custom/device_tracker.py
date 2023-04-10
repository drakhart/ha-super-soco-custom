import logging

from homeassistant.components.device_tracker.config_entry import TrackerEntity

from .const import (
    DATA_MODEL_NAME,
    DEFAULT_FLOAT,
    DEFAULT_INTEGER,
    DEFAULT_STRING,
    DEVICE_TRACKERS,
    DOMAIN,
    MANUFACTURER,
)
from .entity import SuperSocoCustomEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    device_trackers = []

    for (
        id,  # pylint: disable=redefined-builtin
        name,
        source_type,
        latitude_key,
        longitude_key,
        gps_accuracy_key,
        icon,
        extra_attrs,
    ) in DEVICE_TRACKERS:
        if not all(
            k in coordinator.data
            for k in (latitude_key, longitude_key, gps_accuracy_key)
        ):
            _LOGGER.debug("Unable to set up device tracker due to missing data key")
        else:
            device_trackers.append(
                SuperSocoCustomDeviceTracker(
                    config_entry,
                    coordinator,
                    id,
                    name,
                    source_type,
                    latitude_key,
                    longitude_key,
                    gps_accuracy_key,
                    icon,
                    extra_attrs,
                )
            )

    async_add_entities(device_trackers)


class SuperSocoCustomDeviceTracker(SuperSocoCustomEntity, TrackerEntity):
    def __init__(
        self,
        config_entry,
        coordinator,
        id,  # pylint: disable=redefined-builtin
        name,
        source_type,
        latitude_key,
        longitude_key,
        gps_accuracy_key,
        icon,
        extra_attrs,
    ):
        super().__init__(config_entry, coordinator)
        self._id = id
        self._name = name
        self._source_type = source_type
        self._latitude_key = latitude_key
        self._longitude_key = longitude_key
        self._gps_accuracy_key = gps_accuracy_key
        self._icon = icon
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
    def name(self):
        return self._name

    @property
    def source_type(self):
        return self._source_type

    @property
    def latitude(self):
        return self.coordinator.data.get(self._latitude_key, DEFAULT_FLOAT)

    @property
    def longitude(self):
        return self.coordinator.data.get(self._longitude_key, DEFAULT_FLOAT)

    @property
    def gps_accuracy(self):
        return self.coordinator.data.get(self._gps_accuracy_key, DEFAULT_INTEGER)

    @property
    def icon(self):
        return self._icon

    @property
    def extra_state_attributes(self):
        if type(self._extra_attrs) is dict:
            extra_attrs = {}

            for key, value in self._extra_attrs.items():
                extra_attrs[key] = self.coordinator.data.get(value, DEFAULT_STRING)

            return extra_attrs

        return None
